from pathlib import Path
from typing import Optional

from transformers import AutoTokenizer

from src.utils import (
    calculate_metrics,
    dump_json,
    eliminar_repetidos,
    load_all_json_parts,
    load_json,
    post_process,
)


class MorphologicalEvaluator:
    def __init__(
        self,
        tokenizers_paths: list[str],
        data_dir: Optional[Path] = None,
        results_dir: Optional[Path] = None,
    ):
        repository_root = Path(__file__).resolve().parents[1]
        self.data_dir = data_dir or repository_root / "data"
        self.results_dir = results_dir or repository_root / "results"
        self.tokenizers_paths = [
            str(Path(path).resolve()) if Path(path).exists() else path for path in tokenizers_paths
        ]

        self.task1 = load_json(self.data_dir / "1. morph_relevance.json")
        self.task2 = load_all_json_parts(self.data_dir / "2. morph_coherence")
        self.task3 = load_json(self.data_dir / "3. morph_accuracy.json")

    @staticmethod
    def _normalize_token(tokenizer, token: str) -> str:
        if token.startswith("##"):
            token = token[2:]
        decoded = tokenizer.convert_tokens_to_string([token])
        return post_process(decoded.strip())

    @staticmethod
    def _normalize_reference_piece(piece: str) -> str:
        if piece.startswith("##"):
            piece = piece[2:]
        return post_process(piece)

    def _load_tokenizer(self, path: str):
        return AutoTokenizer.from_pretrained(path)

    def _vocabulary(self, tokenizer) -> set[str]:
        vocabulary = set()
        for token in tokenizer.get_vocab():
            normalized = self._normalize_token(tokenizer, token)
            if normalized:
                vocabulary.add(normalized)
        return vocabulary

    def eval_task1(self, output_prefix: str = "task_1") -> dict:
        """Evaluate morphological relevance against each tokenizer vocabulary."""
        results = {}

        for path in self.tokenizers_paths:
            print(f"Evaluating relevance: {path}")
            tokenizer = self._load_tokenizer(path)
            vocab = self._vocabulary(tokenizer)
            results[self._tokenizer_name(path)] = {
                morph_type: calculate_metrics(morphemes, vocab)
                for morph_type, morphemes in self.task1.items()
            }

        self.results_dir.mkdir(parents=True, exist_ok=True)
        dump_json(results, self.results_dir / f"{output_prefix}_results.json")
        return results

    def eval_task2(self, output_prefix: str = "task_2") -> dict:
        """Evaluate how often target morphemes remain intact after tokenization."""
        results = {}

        for path in self.tokenizers_paths:
            tokenizer_name = self._tokenizer_name(path)
            print(f"Evaluating coherence: {path}")
            tokenizer = self._load_tokenizer(path)
            tokenizer_results = {}

            for morph_type, examples in self.task2.items():
                examples = eliminar_repetidos(examples)
                monotoken = 0
                multitoken_correct = 0
                multitoken_incorrect = 0

                for word, morpheme in examples:
                    tokens = [
                        self._normalize_token(tokenizer, token)
                        for token in tokenizer.tokenize(word)
                    ]
                    normalized_morpheme = self._normalize_reference_piece(morpheme)

                    if len(tokens) == 1:
                        monotoken += 1
                    elif normalized_morpheme in tokens:
                        multitoken_correct += 1
                    else:
                        multitoken_incorrect += 1

                total = len(examples)
                tokenizer_results[morph_type] = {
                    "total": total,
                    "monotoken": self._percentage(monotoken, total),
                    "multitoken_correct": self._percentage(multitoken_correct, total),
                    "multitoken_incorrect": self._percentage(multitoken_incorrect, total),
                }

            results[tokenizer_name] = tokenizer_results

        self.results_dir.mkdir(parents=True, exist_ok=True)
        dump_json(results, self.results_dir / f"{output_prefix}_results.json")
        return results

    def eval_tokenizer(self, path: str) -> tuple[float, dict]:
        """Compare tokenizer segmentations with all gold POS-tag segmentations."""
        tokenizer = self._load_tokenizer(path)
        vocab = self._vocabulary(tokenizer)
        correct = 0
        errors = {
            "under_segmented": [],
            "over_segmented": [],
            "unavailable_reference_subword": [],
            "boundary_mismatch": [],
        }

        for entry in self.task3:
            word, gold_by_pos = entry
            gold_segmentations = [
                [self._normalize_reference_piece(piece) for piece in segmentation]
                for segmentation in gold_by_pos.values()
            ]
            predicted = [
                self._normalize_token(tokenizer, token)
                for token in tokenizer.tokenize(word)
            ]

            if predicted in gold_segmentations:
                correct += 1
                continue

            if len(predicted) == 1 and any(len(gold) > 1 for gold in gold_segmentations):
                category = "under_segmented"
            elif len(predicted) > 1 and any(len(gold) == 1 for gold in gold_segmentations):
                category = "over_segmented"
            elif not any(all(piece in vocab for piece in gold) for gold in gold_segmentations):
                category = "unavailable_reference_subword"
            else:
                category = "boundary_mismatch"

            errors[category].append(
                {
                    "word": word,
                    "predicted": predicted,
                    "gold_segmentations": gold_segmentations,
                }
            )

        total = len(self.task3)
        error_summary = {
            "total": total,
            "counts": {category: len(examples) for category, examples in errors.items()},
            "examples": errors,
        }
        return (correct / total if total else 0.0), error_summary

    def eval_task3(self, output_prefix: str = "task_3") -> tuple[dict, dict]:
        results = {}
        all_errors = {}

        for path in self.tokenizers_paths:
            tokenizer_name = self._tokenizer_name(path)
            print(f"Evaluating accuracy: {path}")
            score, errors = self.eval_tokenizer(path)
            correct = len(self.task3) - sum(errors["counts"].values())
            results[tokenizer_name] = {
                "accuracy": round(score * 100, 2),
                "correct": correct,
                "total": len(self.task3),
            }
            all_errors[tokenizer_name] = errors

        self.results_dir.mkdir(parents=True, exist_ok=True)
        dump_json(results, self.results_dir / f"{output_prefix}_results.json")
        dump_json(all_errors, self.results_dir / f"{output_prefix}_errors.json")
        return results, all_errors

    @staticmethod
    def _percentage(count: int, total: int) -> str:
        return f"{(count / total * 100) if total else 0:.2f}%"

    @staticmethod
    def _tokenizer_name(path: str) -> str:
        tokenizer_path = Path(path)
        return f"{tokenizer_path.parent.name}/{tokenizer_path.name}"

    def full_eval(self) -> dict:
        return {
            "morphological_relevance": self.eval_task1(),
            "morphological_coherence": self.eval_task2(),
            "morphological_accuracy": self.eval_task3()[0],
        }
