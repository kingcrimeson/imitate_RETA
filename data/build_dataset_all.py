import argparse
import operator


def build_entity2type_from_whole_dataset(indir, all_training_testing_entities, grain, atLeast):
    black_listed_types = {"/type/common.topic": 1, "/type/base.type_ontology.non_agent": 1,
                          "/type/base.type_ontology.abstract": 1, "/type/base.type_ontology.inanimate": 1,
                          "/type/common.document": 1, "/type/base.type_ontology.physically_instantiable": 1,
                          "/type/base.type_ontology.agent": 1, "/type/base.type_ontology.animate": 1,
                          "/type/type.namespace": 1, "/type/type.content": 1, "/type/type.content_import": 1,
                          "/type/measurement_unit.dated_integer": 1, "/type/media_common.cataloged_instance": 1,
                          "/type/common.image": 1, "/type/common.resource": 1, "/type/measurement_unit.rect_size": 1,
                          "/type/Q4167836": 1, "/type/Q21286738": 1}
    entity2types = {}
    type2frequency = {}
    f = open('type.object.type.txt', "r")
    for line_number, line in enumerate(f):
        splitted_line = line.strip().split("\t")
        if grain == "small":
            entity_type = "/type/" + splitted_line[2]
        elif grain == "big":
            entity_type = "/type/" + splitted_line[2].split(".")[0]
        if entity_type not in type2frequency:
            type2frequency[entity_type] = 1
        else:
            type2frequency[entity_type] += 1
    f.close()
    # 如果频率小于阈值，将其加入黑名单（不使用）
    type2frequency_sorted = sorted(type2frequency.items(), key=operator.itemgetter(1), reverse=True)
    for type_freq in type2frequency_sorted:
        type = type_freq[0]
        freq = int(type_freq[1])
        # print(freq)
        if freq < atLeast:
            print("adding", type, "in the blacklist (freq", freq, ")")
            black_listed_types[type] = 1
    f = open('type.object.type.txt', "r")
    for line_number, line in enumerate(f):
        splitted_line = line.strip().split("\t")
        entity_name = "/entity/" + splitted_line[0]
        if grain == "small":
            entity_type = "/type/" + splitted_line[2]
        elif grain == "big":
            entity_type = "/type/" + splitted_line[2].split(".")[0]
        if entity_type not in black_listed_types and entity_name in all_training_testing_entities:
            if entity_name not in entity2types:
                entity2types[entity_name] = []
            if entity_type not in entity2types[entity_name]:
                entity2types[entity_name].append(entity_type)
    f.close()

    output = open(indir + '/entity2types_tt_' + grain + '.txt', 'w')
    all_types = {}
    for e in entity2types:
        types = entity2types[e]
        for type in types:
            output.write(e + "\t" + type + "\n")
            all_types[type] = 1  # just counting the unique number of types
    output.close()
    print("total number of unique types:", len(all_types))

    return entity2types


## MAIN
parser = argparse.ArgumentParser(description="Data preprocessing path")
parser.add_argument('--indir', type=str, default="JF17k", help='Input dir of train, test and valid data')
parser.add_argument("--grain", type=str, default="big", help="the grain of types")
parser.add_argument('--atLeast', type=int, default=2, help="the minimum of type number")
args = parser.parse_args()

# build type2relation2type ---------------------------------------------------------
all_training_testing_entities = {}
train_test_valid = ["train", "test"]
for tt in train_test_valid:
    with open(args.indir + "/" + tt + ".txt") as train_test_file:
        for line in train_test_file:
            splitted_line = line.strip().split()
            h = splitted_line[0]
            t = splitted_line[1]
            all_training_testing_entities[h] = 1
            all_training_testing_entities[t] = 1
    train_test_file.close()

entity2types_tt = build_entity2type_from_whole_dataset(args.indir, all_training_testing_entities, args.grain, args.atLeast)

output_file = open(args.indir + "/type2relation2type_tt_" + args.grain + ".txt", "w")
for tt in train_test_valid:
    with open(args.indir + "/" + tt + ".txt") as train_test_file:
        for line in train_test_file:
            splitted_line = line.strip().split()
            h = splitted_line[0]
            t = splitted_line[1]
            r = splitted_line[2]

            if h in entity2types_tt and t in entity2types_tt:
                head_types = entity2types_tt[h]
                tail_types = entity2types_tt[t]

                for h_type in head_types:
                    for t_type in tail_types:
                        output_file.write(h_type + "\t" + r + "\t" + t_type + "\n")

    train_test_file.close()
output_file.close()
# build type2relation2type ---------------------------------------------------------
