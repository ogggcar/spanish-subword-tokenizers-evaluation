from src.morphological_evaluator import MorphologicalEvaluator

if __name__ == "__main__":    
    tokenizers = ["dccuchile/bert-base-spanish-wwm-uncased"]
    evaluator = MorphologicalEvaluator(tokenizers_paths=tokenizers)
    evaluator.full_eval()