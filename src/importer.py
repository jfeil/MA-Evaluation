import json
import hashlib
import sys
import os

from database import Definition, DefinitionGenerator, Question, engine
from sqlalchemy.orm import Session
from tqdm.auto import tqdm

if len(sys.argv) < 2:
    print("Pass filename[s] as argument!")
    sys.exit(1)

for path in tqdm(sys.argv[1:]):
    if not os.path.exists(path):
        print(f"{path} is invalid!")
        sys.exit(1)

    with Session(engine) as sess, open(path) as file:
        input_data = json.load(file)

        gt_gen = sess.get(DefinitionGenerator, 'd7d58f75-2211-41ed-b1ab-7f2e1a295d09')
        if not gt_gen:
            gt_gen = DefinitionGenerator(id="d7d58f75-2211-41ed-b1ab-7f2e1a295d09", type="GT", name="!GT!")
            sess.add(gt_gen)

        model_information = input_data['model_information']

        generator = DefinitionGenerator(type=model_information['type'],
                                        name=model_information['name'],
                                        example_prompt=model_information['example_prompt'],
                                        question_prompt=model_information['question_prompt'],
                                        system_prompt=model_information['system_prompt'])
        sess.add(generator)

        questions = []
        new_datapoints = []
        for datapoint in tqdm(input_data['data'], leave=False):
            title = datapoint[1]['title']
            context_word = datapoint[1]['context_word']
            context_sentence = datapoint[1]['context_sentence']

            question_hash = hashlib.sha1(f"{title}{context_word}{context_sentence}".encode()).hexdigest()
            question = sess.get(Question, question_hash)
            if not question:
                question = Question(
                    id=question_hash,
                    title=title,
                    context_word=context_word,
                    context_sentence=context_sentence
                )
                sess.add(question)
                sess.commit()

                gt = Definition(
                    generator_id=gt_gen.id,
                    question_id=question.id,
                    text=datapoint[2]
                )
                sess.add(gt)
                sess.commit()

            pred = Definition(
                generator_id=generator.id,
                question_id=question.id,
                text=datapoint[3]
            )

            sess.add(pred)
            sess.commit()
