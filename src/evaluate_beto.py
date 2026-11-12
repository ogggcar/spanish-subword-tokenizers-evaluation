from src.morphological_evaluator import MorphologicalEvaluator


if __name__ == "__main__":
    evaluator = MorphologicalEvaluator(
        tokenizers_paths=["dccuchile/bert-base-spanish-wwm-uncased"]
    )
    evaluator.eval_task1(output_prefix="task_1_beto")
    evaluator.eval_task2(output_prefix="task_2_beto")
    evaluator.eval_task3(output_prefix="task_3_beto")
