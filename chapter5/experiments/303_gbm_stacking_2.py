from pathlib import Path

import pandas as pd

from common.constants import NUM_PROCESSES, OUTPUT_DIR, TRAIN_CSV_PATH
from common.utils import compute_weights
from experiments.gbm_common import run_kfold
from features.decomposition import (
    DecompositionType,
    VectorizerType,
    build_decomposition_features,
)
from features.edit_distance import build_edit_distance_features
from features.graph import (
    build_graph_connected_component_features,
    build_graph_link_prediction_features,
    build_graph_node_features,
)
from features.length import build_length_features
from features.magic import build_magic_features
from features.match import build_match_features
from features.oof import build_oof_features
from features.word_vector import (
    build_farthest_word_distance_features,
    build_wmd_features,
)
from texts.preprocessing import EmbeddingKey, PreprocessingKey, StopwordsKey

model_params = {
    "objective": "binary",
    "metric": "binary_logloss",
    "boosting": "gbdt",
    "num_leaves": 32,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "feature_fraction": 0.8,
    "learning_rate": 0.1,
    "seed": 1,
    "num_threads": NUM_PROCESSES,
}

trn_df = pd.read_csv(TRAIN_CSV_PATH, na_filter=False)
features = pd.concat(
    [
        build_match_features(
            PreprocessingKey.NLTK_STEMMING, StopwordsKey.NLTK_STEMMED, 1
        ),
        build_match_features(
            PreprocessingKey.NLTK_STEMMING, StopwordsKey.NLTK_STEMMED, 2
        ),
        build_match_features(
            PreprocessingKey.SPACE_TOKENIZATION, StopwordsKey.NLTK, 1
        ),
        build_match_features(
            PreprocessingKey.SPACE_TOKENIZATION, StopwordsKey.NLTK, 2
        ),
        build_length_features(
            PreprocessingKey.NLTK_STEMMING, StopwordsKey.NLTK_STEMMED, 1
        ),
        build_length_features(
            PreprocessingKey.NLTK_STEMMING, StopwordsKey.NLTK_STEMMED, 2
        ),
        build_length_features(
            PreprocessingKey.SPACE_TOKENIZATION, StopwordsKey.NLTK, 1
        ),
        build_length_features(
            PreprocessingKey.SPACE_TOKENIZATION, StopwordsKey.NLTK, 2
        ),
        build_edit_distance_features(
            PreprocessingKey.NLTK_STEMMING, StopwordsKey.NONE
        ),
        build_edit_distance_features(
            PreprocessingKey.SPACE_TOKENIZATION, StopwordsKey.NONE
        ),
        build_wmd_features(
            PreprocessingKey.NLTK_TOKENIZATION,
            StopwordsKey.NLTK,
            EmbeddingKey.GLOVE,
            normalize=True,
        ),
        build_wmd_features(
            PreprocessingKey.NLTK_TOKENIZATION,
            StopwordsKey.NLTK,
            EmbeddingKey.GLOVE,
            normalize=False,
        ),
        build_farthest_word_distance_features(
            PreprocessingKey.NLTK_TOKENIZATION,
            StopwordsKey.NLTK,
            EmbeddingKey.GLOVE,
            metric="cosine",
            normalize=True,
        ),
        build_farthest_word_distance_features(
            PreprocessingKey.NLTK_TOKENIZATION,
            StopwordsKey.NLTK,
            EmbeddingKey.GLOVE,
            metric="euclidean",
            normalize=True,
        ),
        build_farthest_word_distance_features(
            PreprocessingKey.NLTK_TOKENIZATION,
            StopwordsKey.NLTK,
            EmbeddingKey.GLOVE,
            metric="euclidean",
            normalize=False,
        ),
        build_decomposition_features(
            PreprocessingKey.NLTK_STEMMING,
            StopwordsKey.NLTK_STEMMED,
            VectorizerType.COUNT,
            DecompositionType.SVD,
            n_components=30,
            ngram_range=(1, 2),
        ),
        build_decomposition_features(
            PreprocessingKey.NLTK_STEMMING,
            StopwordsKey.NLTK_STEMMED,
            VectorizerType.TFIDF_NONE,
            DecompositionType.SVD,
            n_components=30,
            ngram_range=(1, 2),
        ),
        build_magic_features(),
        build_graph_link_prediction_features(),
        build_graph_node_features(),
        build_graph_connected_component_features(),
        build_oof_features("009_gbm_graph_lr-3e-2"),
        build_oof_features("102_rnn_full_features"),
        build_oof_features("204_bert_concat_last4cls"),
        build_oof_features("301_roberta_full_features"),
        build_oof_features("302_deberta_full_features"),
    ],
    axis=1,
)
save_dir = OUTPUT_DIR / Path(__file__).stem
save_dir.mkdir(exist_ok=True, parents=True)
weights = compute_weights(trn_df.is_duplicate, 0.174)
run_kfold(
    features=features,
    trn_targets=trn_df.is_duplicate,
    n_splits=5,
    save_dir=save_dir,
    model_params=model_params,
    weights=weights,
)
