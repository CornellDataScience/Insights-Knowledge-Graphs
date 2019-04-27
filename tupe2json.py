import json

filepath = './detail_tuples.txt'





def make_one_node(id, name):
    new_node = dict()
    new_node['id'] = id
    new_node['name'] = name
    return new_node


def make_all_nodes():
    node_set = set()
    link_set = set()

    with open(filepath) as fp:
        for line in fp:
            arg_1 = line[1:line.find(',')]
            arg_2 = line[line.find(',') + 1:line.rfind(',')]
            rel = line[line.rfind(',') + 1:-1]
            node_set.add(make_one_node(int(arg_1), ))
            node_set.add(arg_2)



    return json.dumps(node_list)













node_list = make_all_nodes()

# output the json file
with open('graph.json', 'w') as outfile:
    json.dump(node_list, outfile)

# reads in the outputted json file and make sure it works
with open('graph.json', encoding='utf-8') as data_file:
    node_list_read = json.loads(data_file.read())

print(node_list_read)






