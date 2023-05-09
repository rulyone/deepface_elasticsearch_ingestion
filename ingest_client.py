from elasticsearch import Elasticsearch, helpers
import json

from deepface import DeepFace
from retinaface import RetinaFace


def load_presidents():
    with open('presidents.json', 'r', encoding='utf-8') as fp:
        return json.load(fp)
    
def create_docs_from_image(president_name, image_path, index_name):
    faces = RetinaFace.extract_faces(image_path)
    
    for face in faces:
        face_analysis = DeepFace.analyze(face, detector_backend = 'skip')
        doc = {
            '_index': index_name,
            '_source': {
                'deepface_analysis': face_analysis,
                'president_name': president_name,
                'filename': image_path
            }
        }
        yield doc

es_client = Elasticsearch(hosts="http://localhost:9200")

# We read presidents.json into a dict
presidents = load_presidents()

index_name = 'presidents_of_chile'

# Iterate each president
for president_name in presidents:
    # Iterate each image of the president
    for image in presidents[president_name]:
        # We insert to elasticsearch
        helpers.bulk(es_client, create_docs_from_image(president_name, image, index_name))

result = es_client.count(index=index_name)
print(result)

