import os
import json
import requests

from tqdm import tqdm

file_extensions = {".txt", ".org", ".py"}


def _read_files(folder):
    text_files = []
    for root, dir, files in os.walk(folder):
        for file in files:
            if os.path.splitext(file)[-1] in file_extensions:
                with open(os.path.join(root, file), "r") as f:
                    text_files.append(
                        {"chunk_metadata": file, "chunk": f.read()}
                    )

    return text_files


def _summarize_text(texts):
    summaries = {}
    url = "https://api.berri.ai/create_app"
    query_api = "https://api.berri.ai/query"
    for note in tqdm(texts):
        data = {
            "user_email": "cpmdump@gmail.com",
            "data_source": json.dumps([note]),
        }
        app_response = requests.post(url, data=data)

        if not app_response.ok:
            print(app_response.text)
            continue
        query_params = {
            "user_email": app_response.json()["account_email"],
            "instance_id": app_response.json()["instance_id"],
            "query": f"Summarize the note {note['chunk_metadata']}",
            "model": "gpt-3.5-turbo",
        }
        response = requests.get(query_api, params=query_params)
        summaries[note["chunk_metadata"]] = response.json()["response"]
    return summaries


def _generate_main_instance(summaries):
    data_dump = json.dumps(
        [
            {"chunk_metadata": name, "chunk": summary}
            for name, summary in summaries.items()
        ]
    )
    url = "https://api.berri.ai/create_app"
    data = {"user_email": "cpmdump@gmail.com", "data_source": data_dump}
    instance_response = requests.post(url, data=data)
    if instance_response.ok:
        return instance_response.json()
    else:
        raise


def _find_related(instance, querynotes):
    related_queries = {}
    query_api = "https://api.berri.ai/query"
    for querynote in tqdm(querynotes):
        query_params = {
            "user_email": instance["account_email"],
            "instance_id": instance["instance_id"],
            "query": f"Which note other than {querynote} talks about similar topics as {querynote}",
            "model": "gpt-3.5-turbo",
        }
        response = requests.get(query_api, params=query_params)
        related_queries[querynote] = [
            x["doc_metadata"] for x in response.json()["references"]
        ]
    return related_queries


def generate_links(folder, output):
    texts = _read_files(folder)
    summaries = _summarize_text(texts)
    instance = _generate_main_instance(summaries)
    related_queries = _find_related(instance, summaries.keys())
    links = {}
    for query, related_notes in related_queries.items():
        notes = list(set(related_notes) - set([query]))
        links[query] = notes

    if output is not None:
        json.dump(links, open(output, "w"), indent=4)
    return links
