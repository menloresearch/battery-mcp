from ChatBattery.domain_agent import Domain_Agent
from ChatBattery.search_agent import Search_Agent
from ChatBattery.decision_agent import Decision_Agent
from ChatBattery.retrieval_agent import Retrieval_Agent
import json
import os
import pandas as pd
from battery_mcp.db import load_retrieval_DB
# def load_retrieval_DB():
#     DB = pd.read_csv("https://github.com/chao1224/ChatBattery/blob/main/data/Li_battery/preprocessed.csv")
#     DB = DB[['formula']]
#     return DB

retrieval_DB = load_retrieval_DB()


def calculate_material_capacity(query: str) -> float:
    return Domain_Agent.calculate_theoretical_capacity(query, 101)


def search_material(formula: str, n: int):
    distance_DB = retrieval_DB.copy()
    distance_list = []
    capacity_list = []
    for index, row in distance_DB.iterrows():
        formula_ = row['formula']
        distance = Domain_Agent.distance_function(101, formula_, formula)
        capacity = calculate_material_capacity(formula_)
        distance_list.append(distance)
        capacity_list.append(capacity)
    distance_DB['distance'] = distance_list
    distance_DB['capacity'] = capacity_list

    distance_DB = distance_DB.sort_values(by=['distance'], ascending=True)
    distance_DB = distance_DB.to_dict(orient='records')
    materials = []
    materials_formula = []
    for material in distance_DB:
        if material["formula"] in materials_formula:
            continue
        else:
            materials_formula.append(material["formula"])
            materials.append(material)
        if len(materials) == n:
            break
    return str(materials)


def verify_input_material(original_material: str) -> str:
    """
    Tool to check if the input material from user is valid or not
    - The original_material is the material from user's input.
    """
    if not Search_Agent.ICSD_search(original_material, retrieval_DB["formula"].tolist()):
        retrieved_battery, retrieved_capacity = Retrieval_Agent.retrieve_with_domain_feedback(
            101, retrieval_DB, original_material, original_material)
        return f"The material {original_material} does not exist in Database, this might not a valid material. Can you chose other materials to start with?\n {retrieved_battery} is the most relevent material from the Database, you might want to use this as the input material"
    else:
        return "The input material is valid and exists in database"


def battery_material_validation(original_material: str, query: str) -> str:
    """
    Tool to parse battery material from query then validate the material capacity using for battery. 
    - The original_material is the material from user's input.
    - The query contains proposed materials separated by commas, e.g "Li2B4O7, Li1.06Ti2O4, Li2H0.9996N1. Including previous valid and novel materials and new proposed materials"
    """

    materials = query.split(",")
    materials = [x.strip() for x in materials]
    input_value = Domain_Agent.calculate_theoretical_capacity(
        original_material, 101)
    content = "Input battery is {} with capacity {:.3f}".format(
        original_material, input_value)
    result = {}
    for generated_battery in materials:
        result[generated_battery] = "novel"
        if Search_Agent.ICSD_search(generated_battery, retrieval_DB["formula"].tolist()):
            result[generated_battery] = "not novel"
        if Search_Agent.MP_search(generated_battery):
            result[generated_battery] = "not novel"

    answer_list = Decision_Agent.decide_pairs(
        original_material, materials, 101)
    for generated_battery, output_value, answer in answer_list:
        if result[generated_battery] == "not novel":
            content += "\n* Candidate optimized battery {} is not novel".format(
                generated_battery)
        else:
            content += "\n* Candidate optimized battery {} is novel".format(
                generated_battery)
        if answer:
            content += " and valid, with capacity {:.3f}".format(output_value)
        else:
            content += " and invalid, with capacity {:.3f}".format(
                output_value)
        if result[generated_battery] == "novel":
            if not answer:
                try:
                    retrieved_battery, retrieved_capacity = Retrieval_Agent.retrieve_with_domain_feedback(
                        101, retrieval_DB, original_material, generated_battery)
                    retrieved_content = "\nRetrieved battery {} with capacity {:.3f} is the most similar to the candidate optimized battery {} and serves as a valid optimization to the input battery, you must proposed different material base on this hint.".format(
                        retrieved_battery, retrieved_capacity, generated_battery)
                except:
                    retrieved_battery = None
                    retrieved_content = "\nNo valid battery is retrieved is similar to candidate optimized battery {}.".format(
                        generated_battery)
                content += retrieved_content
        content += "\n------------------------------------------\n"
    return content
