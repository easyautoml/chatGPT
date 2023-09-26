from pyvis.network import Network

import re
import json


def extract_nodes(nodes):
    """
    Extract nodes
    """
    json_regex = "\{(.*?)\}"

    result = []
    for i, node in enumerate(nodes):
        node_detail = node.split(",")
        name = node_detail[0].strip().replace('"', "")
        label = node_detail[1].strip().replace('"', "")
        properties = re.search(json_regex, node)

        if properties is None or properties.group(1).strip() == "":
            properties = "{}"
        else:
            properties = properties.group(0)

        properties = properties.replace("True", "true").replace("False", "false")
        properties = json.loads(properties)

        result.append({"key": i, "name": name, "label": label, "properties": properties})

    return result


def extract_relationships(relationships, nodes):
    """
    Extract relationship between nodes
    """
    json_regex = '\\{(.*?)\\}'

    result = []
    for relation in relationships:
        relation = relation.replace("True", "true").replace("False", "false")

        relation_lst = relation.split(",")
        if len(relation) < 3:
            continue

        start_name = relation_lst[0].strip().replace('"', "")
        start_key = get_key_node_by_name(nodes, start_name)

        end_name = relation_lst[2].strip().replace('"', "")
        end_key = get_key_node_by_name(nodes, end_name)

        if start_key is None or end_key is None:
            continue

        node_type = relation_lst[1].strip().replace('"', "")

        properties = re.search(json_regex, relation)
        if properties is None or properties.group(0).strip() == "":
            properties = "{}"
        else:
            properties = properties.group(0)
        properties = json.loads(properties)

        result.append(
            {"start_name": start_name, "start_key": start_key,
             "end_name": end_name, "end_key": end_key,
             "type": node_type, "properties": properties}
        )
    return result


def extract_nodes_relationship(result):
    regex = "Nodes:\s+(.*?)\s?\s?Relationships:\s+(.*)"
    internal_regex = "\[(.*?)\]"

    nodes = []
    relationships = []

    for row in result:
        parsing = re.match(regex, row, flags=re.S)

        if parsing is None:
            continue

        raw_nodes = str(parsing.group(1))
        raw_relationship = parsing.group(2)

        nodes.extend(re.findall(internal_regex, raw_nodes))
        relationships.extend(re.findall(internal_regex, raw_relationship))

    nodes = extract_nodes(nodes)
    relationships = extract_relationships(relationships, nodes)

    return dict(
        nodes=nodes,
        relationships=relationships
    )


def get_key_node_by_name(nodes, name):
    matching_nodes = [node for node in nodes if node.get('name') == name]
    return matching_nodes[0].get("key") if matching_nodes else None


def assign_category_colors(categories):
    color_hex_mapping = {}
    color_palette = [
        '#1ABC9C', '#2ECC71', '#3498DB', '#9B59B6',
        '#34495E', '#16A085', '#27AE60', '#2980B9',
        '#8E44AD', '#2C3E50', '#F1C40F', '#E67E22'
    ]

    for i, category in enumerate(categories):
        color_hex_mapping[category] = color_palette[i % len(color_palette)]

    return color_hex_mapping


def visualize_nodes(result):
    result = extract_nodes_relationship(result)

    net = Network(notebook=True,
                  cdn_resources="remote",
                  bgcolor="#222222",
                  font_color="white",
                  height="750px",
                  width="100%",
                  select_menu=False,
                  filter_menu=False,
                  )

    node_type = list(set([node.get("label") for node in result.get("nodes")]))
    type_colors = assign_category_colors(node_type)

    node_keys = [node.get('key') for node in result.get("nodes")]

    node_labels = [node.get('name') for node in result.get("nodes")]

    node_color = [type_colors.get(node.get("label")) for node in result.get("nodes")]
    node_title = [str(node.get("properties")).replace("', '", "\r\n").replace("'", "").replace("{", "").replace("}", "")
                  for node in result.get("nodes")]

    net.add_nodes(node_keys, label=node_labels, color=node_color, title=node_title)

    for relation in result.get("relationships"):
        net.add_edge(relation.get("start_key"), to=relation.get("end_key"), title=relation.get("type"))

    net.show('edges.html')
