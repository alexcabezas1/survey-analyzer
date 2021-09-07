import csv
from contextlib import contextmanager
from collections import OrderedDict
from argparse import ArgumentParser


RESOURCES_PATH = 'resources'
SURVEY_DEFAULT_PATH = 'resources/encuesta.csv'
QUESTIONS_RANGE_START = 1
QUESTIONS_RANGE_END = -1


def get_filepath():
    return SURVEY_DEFAULT_PATH


@contextmanager
def read_csv():
    filepath = get_filepath()
    file = open(filepath, 'r')
    reader = csv.reader(file, delimiter=',', quotechar='"')

    try:
        yield reader
    finally:
        file.close()    


def get_questions():
    questions = []
    with read_csv() as reader:
        headers = next(reader)
        questions = headers[QUESTIONS_RANGE_START:QUESTIONS_RANGE_END]

    return questions


def possible_anwsers():
    answers = {}
    with read_csv() as reader:
        headers = next(reader)
        questions = headers[QUESTIONS_RANGE_START:QUESTIONS_RANGE_END]
        for row in reader:
            for index, answer in enumerate(row[QUESTIONS_RANGE_START:QUESTIONS_RANGE_END]):
                if len(answer) == 0:
                    continue
                
                values = {k: '' for k in answer.split(";")}

                try:
                    answers[questions[index]].update(values)
                except KeyError:
                    answers[questions[index]] = OrderedDict(values)
    return answers


def read_survey():
    with read_csv() as reader:
        next(reader)
        for row in reader:
            yield row[QUESTIONS_RANGE_START:QUESTIONS_RANGE_END]


def id_to_qa(q_a_pair, questions_with_answers):
    pair = q_a_pair.split(":")
    try:
        question_index = int(pair[0][1:]) - 1
        answer_index = int(pair[1][1:]) - 1
    except ValueError:
        return (None, None)
    
    question = list(questions_with_answers.keys())[question_index]
    answer = list(questions_with_answers[question].keys())[answer_index]

    return (question, answer)


def qa_to_id(question, answer, questions_with_answers):
    if not question or not answer:
        return None

    question_index = list(questions_with_answers.keys()).index(question) + 1
    answer_index = list(questions_with_answers[question].keys()).index(answer) + 1
    
    return f"p{question_index}:r{answer_index}"


def groups_definition_parser(definition):
    for line in definition:
        yield line.split(",")


def dummy_per_answer(answers, groups, questions, questions_with_answers, verbose=False):
    dummy = {}

    answer_groups = []
    for i, value in enumerate(answers):
        values = value.split(";")
        for answer in values: 
            if not answer:
                continue
            qa_id = qa_to_id(questions[i], answer, questions_with_answers)
            answer_groups.append(qa_id)
            if verbose:
                print(qa_id, questions[i], answer)
    
    for grp_limit in groups:
        count = 0
        tmp_dummy = {}
        for grp in grp_limit:
            if grp in answer_groups:
                count += 1
                tmp_dummy[grp] = 1
        if count == len(grp_limit):
            dummy.update(tmp_dummy)

    if verbose:
        print(answers)
        print(">>", answer_groups)
        print(dummy)
    return dummy


def explode_groups_def(group_def):
    for line in group_def:
        if len(line) == 0:
            continue
        path = ''
        group = line.split(",")
        for gr in group:
            path += gr + ","
            yield path[:-1]


def show_questions_answers_catalog(questions_with_answers):
    for q, v in questions_with_answers.items():
        print(q)
        for a in v.keys():
            print(qa_to_id(q, a, questions_with_answers), '->', a)
        print("")


def main(opts):
    if opts.verbose:
        print(opts)
        print()

    if opts.file:
        global get_filepath
        get_filepath = lambda: opts.file

    questions_with_answers = possible_anwsers()
    questions = get_questions()

    if opts.testing:
        q, a = id_to_qa("p17:r4", questions_with_answers)
        print(q, a)
        pair = qa_to_id(q, a, questions_with_answers)
        print(pair)
        print(id_to_qa(pair, questions_with_answers))

        test = [
            '26 a 35 años', 'Sí', 'Sí', 'Mensualmente', 
            'Llevando los productos a un centro de reciclaje o similar', 
            'Plástico;Vidrio;Envases;Materiales electrónicos;Pilas;Metales;Telas', 
            '9', 'No', '', '', '', 'Sí', 'No', 'No conozco nada', 'Tengo una noción basica', 
            'Bastante', 'Sí', 'Sí', 'Sí'
        ]
        groups = list(groups_definition_parser(['p2:r1,p3:r2,p9:r1', 'p2:r1,p3:r2,p9:r4']))
        print(
            dummy_per_answer(test, groups, questions, questions_with_answers, True))
    
    if opts.list:
        show_questions_answers_catalog(questions_with_answers)
        return

    # [
    #     "p2:r1,p3:r1,p4:r5",
    #     "p2:r1,p3:r1,p4:r3",
    #     "p2:r1,p3:r2,p9:r1"
    # ]

    groups_def = opts.groups
    expanded_groups_def = set(explode_groups_def(groups_def))
    groups = list(groups_definition_parser(expanded_groups_def))
    if opts.verbose:
        for gr in expanded_groups_def:
            print(gr)
        print(groups)
        print()

    dummies = []
    reader = read_survey()
    for i, row in enumerate(reader):
        dummy = dummy_per_answer(row, groups, questions, questions_with_answers)
        if dummy:
            dummies.append(dummy)
    
    metrics = {}
    for dummy in dummies:
        metric = ''
        qa_included = []
        for qa in dummy:
            for grp_limit in groups:
                if qa in grp_limit and not qa in qa_included:
                    if len(metric) == 0:
                        metric += qa
                    else:
                        metric += "," + qa

                    try:
                        metrics[metric] += 1
                    except:
                        metrics[metric] = 1

                    qa_included.append(qa)

    for k, v in sorted(metrics.items()):
        print(k, '=', v)
        pairs = k.split(",")
        question, answer = id_to_qa(pairs[len(pairs)-1], questions_with_answers)
        print("-" * len(pairs[:-1]), question, f"Re: {answer} ->", v)
        print("")


if __name__ == '__main__':
    parser = ArgumentParser(description="Survey Analizer", fromfile_prefix_chars='@')
    parser.add_argument('-g', '--groups', action='store',
                        type=str, nargs='+', default=['p1:r1', 'p2:r1,p3:r1,p4:r3'],
                        help="List of groups 'question:answer' pairs. Examples: -i p2:r1,p4:r1, -i p2:r1,p3:r1,p4:r5")
    parser.add_argument('-l', '--list', action='store_true', help="Index of questions and answer. To know question & answer identifier.")
    parser.add_argument('-t', '--testing', action='store_true', help='Testing mode')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbosing mode')
    parser.add_argument('-f', '--file', action='store', help='Survey file', default=SURVEY_DEFAULT_PATH)
    opts = parser.parse_args()

    main(opts)
