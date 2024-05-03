from setup import create_opneaiclient
from datetime import datetime
import time
import json
import os
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor

def obj_to_dict(obj):
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return {k: obj_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [obj_to_dict(elem) for elem in obj]
    else:
        return {attr: obj_to_dict(getattr(obj, attr)) for attr in vars(obj)}

client = create_opneaiclient()

# ----------------- Ad-hoc processing -----------------
# state = client.fine_tuning.jobs.retrieve("ftjob-S7U3XXqtWCE8OnsKndJIlmZu")
# num_lines_in_train = 466
# json_dict = obj_to_dict(state)
# json_dict['num_lines_in_train'] = num_lines_in_train
# with open(f"/Users/jackieliu/Documents/CODE/cs4701-ai-prac/generate_songs/models/model_ftjob-S7U3XXqtWCE8OnsKndJIlmZu.json", "w") as info_file:
#     info_file.write(json.dumps(json_dict, indent=4))
# sys.exit()
# ----------------- Ad-hoc processing -----------------
# state = client.fine_tuning.jobs.retrieve("ftjob-0vw5EgJfAW55v68iqXMsNpSA")
# for idx, result_file in enumerate(state.result_files):
#     content = client.files.content(result_file)
#     with open(f"/Users/jackieliu/Documents/CODE/cs4701-ai-prac/generate_songs/model_result_files/model_ftjob-0vw5EgJfAW55v68iqXMsNpSA_{idx}.csv", "w") as info_file:
#         info_file.write(content.content.decode())
# sys.exit()
# ----------------- Ad-hoc processing -----------------

SEED = 42

directory = '../data/diff_train_sizes'
files = os.listdir(directory)
MAX_WORKERS = len(files)
BATCH_SIZE = 3
SLEEP_TIME = 15
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def wait_for_finetune_success(fine_tuning_job_id, num_lines_in_train):
    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(10)
    state = client.fine_tuning.jobs.retrieve(fine_tuning_job_id)
    print(f"model {fine_tuning_job_id} finetuning is at status:", state.status)
    while state.status != 'succeeded':
        time.sleep(SLEEP_TIME)
        state = client.fine_tuning.jobs.retrieve(fine_tuning_job_id)
    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    fine_tuning_model_id = state.fine_tuned_model
    hyperparemeters = state.hyperparameters
    trained_tokens = state.trained_tokens
    print(f"model {fine_tuning_job_id} finetuning is at status: {state.status} \n fine_tuned_model: {fine_tuning_model_id} \n hyperparemeters: {hyperparemeters} \n trained_tokens: {trained_tokens} \n start: {start} \n end: {end}")

    json_dict = obj_to_dict(state)
    json_dict['num_lines_in_train'] = num_lines_in_train
    with open(f"/Users/jackieliu/Documents/CODE/cs4701-ai-prac/generate_songs/models/model_{fine_tuning_job_id}.json", "w") as info_file:
        info_file.write(json.dumps(json_dict, indent=4))

    for idx, result_file in enumerate(state.result_files):
        content = client.files.content(result_file)
        with open(f"/Users/jackieliu/Documents/CODE/cs4701-ai-prac/generate_songs/model_result_files/model_ftjob-0vw5EgJfAW55v68iqXMsNpSA_{idx}.csv", "w") as info_file:
            info_file.write(content.content.decode())

async def main():
    loop = asyncio.get_event_loop()
    futures = []
    # Rate limit of 3 requests at once
    # batch1 = ["train_0.85.jsonl", "train_0.2.jsol", "train_0.4.jsonl"]
    # batch1_5 = ["train_0.3.jsonl"]
    batch2 = ["train_0.01.jsonl", "train_1.jsonl"]
    batch3 = ["train_0.7.jsonl", "train_0.05.jsol", "train_0.5.jsonl"]
    # batches = [files[i:i + BATCH_SIZE] for i in range(0, len(files), BATCH_SIZE)]

    async def batch_helper(batch):
        for train_file_name in batch:
            # train_file_name = "train.jsonl"
            train_file_name_path = os.path.join(directory, train_file_name)

            with open(train_file_name_path, 'r') as file:
                lines = file.readlines()
            num_lines_in_train = len(lines)

            res = client.files.create(
                file=open(train_file_name_path, "rb"),
                purpose="fine-tune"
            )
            train_file_id = res.id
            res = client.files.create(
                file=open("../data/val.jsonl", "rb"),
                purpose="fine-tune"
            )
            val_file_id = res.id

            # https://platform.openai.com/docs/api-reference/fine-tuning/create
            # TODO hyperparemeters tuning
            # TODO wandb integration for experiment tracking
            res = client.fine_tuning.jobs.create(
                training_file=train_file_id, 
                model="gpt-3.5-turbo",
                seed=SEED,
                validation_file=val_file_id
            )
            fine_tuning_job_id = res.id
            futures.append(loop.run_in_executor(executor, wait_for_finetune_success, fine_tuning_job_id, num_lines_in_train))
        runtimes = await asyncio.gather(*futures, return_exceptions=True)
        print(runtimes)

    # for batch in batches:
    #     await batch_helper(batch)
    # await batch_helper(batch1) [DONE]
    await batch_helper(batch2) 
    await batch_helper(batch3) 

asyncio.run(main())