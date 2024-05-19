import utilities as utils
import json

class paths:
    offers = 'data\offers\offers.json'
    offers_sbox = 'data\offers\offers_sandbox.json'
    settings = 'data\settings.json'
    backup = 'data/offers/backups'
    backup_folder = 'backup'

import os
import datetime
from pytz import timezone
#* tested
def make_backup(override: bool = True, offers: list = None) -> str:
    """
    Makes a buck up of allegro offers by downloading all data for each offer and storing it in a file.\n
    override = true, will override files in data\\offers\\backups\\backup with new data\n
    override = false, will create a folder with curet time stamp in data\\offers\\backups abd store files there\n
    offers = none, will buck up all offers from data\\offers\\offers.json\n
    offers = list, provide offer numbers to be backed up (numbers must be a str)\n
    returns where the buck up was saved\n
    """
    
    print("Backing up offers...")
    if offers == None:
        with open(paths.offers, mode = 'r') as file:
            offers = json.load(file)
            if isinstance(offers, dict):
                offers = offers.keys()
    save_path = os.path.join(paths.backup, paths.backup_folder)
    if not override:
        #* tested
        #make a nev directory
        time = str(datetime.datetime.now(timezone('Poland')))
        time = time.replace(":",";")
        save_path = os.path.join(paths.backup, time)
        os.mkdir(save_path)
    else:
        #* tested
        #clear directory
        list( map( os.unlink, (os.path.join( save_path,f) for f in os.listdir(save_path)) ) )
    
    length = len(offers)
    c = 0
    for i in offers:
        c += 1
        print(f"{c} of {length}...")
        #get data
        result = utils.Allegro.send("GET", f"/sale/product-offers/{i}")
        file_name = str(i)
        path = os.path.join(save_path, file_name)
        #save data
        with open(path, mode='w') as file:
            json.dump(result, file,indent = 4)
    print("Done!")
    if override:
        return save_path

#* tested
def load(path: str = None):
    """
    Allows for loading offers in a json format to Allegro.\n
    path = none, will load all offers from data\\offers\\backups\\backup to Allegro\n
    path = str, provide a path to a folder from which offers should be loaded\n
    """
    print("Loading buck up...")
    #get dir
    directory = ""
    if path == None:
        #* tested
        directory = os.path.join(paths.backup, paths.backup_folder)
    else:
        #* tested
        p =  os.getcwd()
        directory = os.path.join(p, path)
    
    #* tested
    dir_list = os.listdir(directory)
    length = len(dir_list)
    c = 0
    for filename in dir_list:
        c += 1
        print(f"{c} of {length}...")
        #get data
        f = os.path.join(directory, filename)
        with open(f, mode = 'r') as file:
            offer = json.load(file)
        #load data
        utils.Allegro.send("PATCH", f"/sale/product-offers/{filename}", offer)
    print("Done!")
        
import importlib.util
import shutil

#* tested
def execute_order(instruction: str,offers: list = None, saved_dir: str = None, apply: bool = True):
    """
    Preforms a transformation from given instruction on each offer\n
    instruction = path to a specifically written pythons script (see example script in patens//example)\n
    offers = none, will use offer id's from data\\offers\\offers.json\n
    offers = list, provide offer numbers to be used (numbers must be a str)\n
    saved_dir = none, will download data of each offer fom Alle before applying the transformation\n
    saved_dir = str, provide a path to folder where offers that should be used are\n
    will crate a folder with a time stamp where the instructions are stored in which in the input folder input offers will be stored.\n
    apply = true, will apply edited offers to Allegro\n
    apply = false, will crate a folder with a time stamp where the instructions are stored in which in the output folder results will be stored\n
    """
    print(f"Executing order {instruction} ...")
    #* tested
    #load pattern
    spec = importlib.util.spec_from_file_location(instruction, instruction)
    paten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(paten)

    work_folder = ''
    if saved_dir != None or apply == False:
        #make a nev directory
        dir = os.path.dirname(instruction) 
        time = str(datetime.datetime.now(timezone('Poland')))
        time = time.replace(":",";")
        work_folder = os.path.join(dir, time)
        os.mkdir(work_folder)
    
     #* tested
    selection = offers
    input_dir = ''

    #make a input dir
    if saved_dir != None:
        input_dir = os.path.join(work_folder, 'input')
        p =  os.getcwd()
        saved_dir = os.path.join(p, saved_dir)
        dir_list = os.listdir(saved_dir)
        selection = []
        if offers != None:
            os.mkdir(input_dir)
            #* tested
            for i  in dir_list:
                id = i.replace('.json','')
                if id in offers:
                    shutil.copy(os.path.join(saved_dir,i),input_dir)
                    selection.append(id)
        else:
            #* tested
            shutil.copytree(saved_dir, input_dir)
            selection = dir_list
    else:
        if offers == None:
            #* tested
            with open(paths.offers, mode = 'r') as file:
                offers = json.load(file)
            if isinstance(offers, dict):
                selection = offers.keys()
            else:
                selection = offers
    
    output_dir = ''
    if apply == False:
        output_dir = os.path.join(work_folder, 'output')
        os.mkdir(output_dir)
    
    length = len(selection)
    c = 0

    data = []
    for i in selection:
        c += 1
        print(f"{c} of {length}...")
        #get offer data
        offer_data = {}
        if saved_dir != None:
            #* tested
            path = os.path.join(input_dir,f"{i}.json")
            with open(path, mode = 'r') as file:
                offer_data = json.load(file)
        else:
            #* tested
            offer_data = utils.Allegro.send("GET", f"/sale/product-offers/{i}")
        #run script
        #* tested
        result,data = paten.main(offer_data,data)
        #save result
        if apply:
            #* tested
            utils.Allegro.send("PATCH", f"/sale/product-offers/{i}", result)
        else:
            #* tested
            path = os.path.join(output_dir,i)
            with open(path, mode='w') as file:
                json.dump(result, file,indent = 4)
    print("Done!")

# os.chdir("C:\\Users\\rochz\\Desktop\\Allegro bulk offer editor\\public")
# execute_order('data\patterns\example\example.py', offers=['7751378395'], saved_dir = 'example', apply = False) 