def calculate_raw_materials(item, quantity, recipes):
    if item not in recipes: # if item is not a component, it's a raw material
        return {item: quantity}

    raw_materials = {}

    for component, amount_per_unit in recipes[item].items(): # calculate total amount needed for the component
        total_needed = amount_per_unit * quantity
        sub_materials = calculate_raw_materials(component, total_needed, recipes) # use recursion to break down the component into raw materials
        for raw, raw_qty in sub_materials.items():
            raw_materials[raw] = raw_materials.get(raw, 0) + raw_qty # sum up the quantities of each raw material needed

    return raw_materials


#put your input here
recipes = {
    'SteelSword':  {'SteelIngot': 2, 'LeatherGrip': 1},
    'SteelIngot':  {'IronOre': 3, 'Coal': 2},
    'LeatherGrip': {'Leather': 1, 'String': 2},
    'String':      {'PlantFibers': 3}
}

print(calculate_raw_materials('SteelSword', 5, recipes))