from pathlib import Path

from src.morphological_evaluator import MorphologicalEvaluator


if __name__ == "__main__":
    repository_root = Path(__file__).resolve().parents[1]
    tokenizers = [
        str(repository_root / f"subword_tokenizers_{vocab_size}" / algorithm)
        for vocab_size in (31, 52)
        for algorithm in ("bpe", "wordpiece", "unigram")
    ]
    evaluator = MorphologicalEvaluator(tokenizers_paths=tokenizers)
    evaluator.full_eval()