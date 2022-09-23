import torch
import json
import torch.backends.cudnn as cudnn

import argparse
from trainer import Trainer, TrainingArguments
from preprocess_data import EntityLinkingSet
from logger_config import logger
import wandb

def get_args():
    parser = argparse.ArgumentParser("zero shot entity linker")

    parser.add_argument("--pretrained-model-path", default='pretrained', type=str,
                        help="Path to pretrained transformers.")
    parser.add_argument("--train-documents-file", nargs="+", default=None,
                        help="Path to train documents json file.")
    parser.add_argument("--eval-documents-file", nargs="+", default=None,
                        help="Path to train documents json file.")
    parser.add_argument("--mentions-file", default='zeshel/mentions', type=str,
                        help="Path to mentions json file.")
    parser.add_argument("--tfidf-candidates-file", default='tfidf_candidates/test.json', type=str,
                        help="Path to TFIDF candidates file.")

    parser.add_argument(
        "--split-by-domain", default=False, type=bool,
        help="Split output data file by domain.")

    parser.add_argument("--learning-rate", default=1e-5, type=float,
                        help="learning rate for optimization")
    parser.add_argument("--weight-decay", default=1e-4, type=float,
                        help="weight decay for optimization")
    parser.add_argument("--epochs", default=3, type=int,
                        help="weight decay for optimization")
    parser.add_argument("--train-batch-size", default=128, type=int,
                        help="train batch size")
    parser.add_argument("--eval-batch-size", default=128, type=int,
                        help="train batch size")

    parser.add_argument("--max-seq-length", default=128, type=int, help="Maximum sequence length.")

    parser.add_argument("--num-candidates", default=64, type=int, help="Number of entity candidates.")

    parser.add_argument("--random-seed", default=12345, type=int, help="Random seed for data generation.")

    args = parser.parse_args()
    return args


def main():
    if torch.cuda.device_count() > 0:
        cudnn.benchmark = True

    # with wandb.init(settings=wandb.Settings(start_method="fork"), project="BMKG", entity="marvinpeng", config=vars(args)):
    #     wandb.config.update(args, allow_val_change=True)
    #     trainer = Trainer(args, ngpus_per_node=ngpus_per_node)
    # #     logger.info('Args={}'.format(json.dumps(args.__dict__, ensure_ascii=False, indent=4)))
    #     trainer.train_loop()

    args = get_args()
    train_args = TrainingArguments
    train_dataset = EntityLinkingSet(
                                    pretrained_model_path=args.pretrained_model_path,
                                    document_files=args.train_documents_file,
                                     mentions_files=['zeshel/mentions/test.json'],
                                     tfidf_candidates_file=args.tfidf_candidates_file,
                                     num_candidates=args.num_candidates,
                                     max_seq_length=256,
                                     is_training=True)

    eval_dataset = EntityLinkingSet(
                                    pretrained_model_path=args.pretrained_model_path,
                                    document_files=args.eval_documents_file,
                                   mentions_files=['zeshel/mentions/test.json'],
                                   tfidf_candidates_file=args.tfidf_candidates_file,
                                    num_candidates=args.num_candidates,
                                    max_seq_length=256,
                                   is_training=False)

    trainer = Trainer(
        pretrained_model_path=args.pretrained_model_path,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        train_args=train_args)
    logger.info('Args={}'.format(json.dumps(args.__dict__, ensure_ascii=False, indent=4)))
    trainer.run()

if __name__ == '__main__':
    main()
