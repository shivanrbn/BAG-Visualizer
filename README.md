# BAG Visualizer

This repository contains code for my graduation project, extracting 3D BAG data, calculating the best possible panorama's and images and visualizing this into a 3D model.

## Outlines
The repository will be split into two categories
1. The extraction and calculation part
1. The 3D modeling and visualisation part

### Extraction and calculation
The polygons (3D model data) is stored into a postgres database, which need to be retrieved first before calculations can be done. <br>
There are multiple level of details (LOD) which the 3DBAG supplies, for this project we will primary use LOD 2.2. <br>

#### CLI
There is a CLI (called cli.py) in the extractor map which can be used together with an bag building id (noted as bag_building_id or bag_id) to fetch the polygons and images for a single building.

## Repository structure

The repository is split up into 4 parts:
1. The extractor which extracts the BAG data and gathers images from the extracted data.
1. The bag_visualisation which will contain standalone code to visualize the project
1. The models which are used to query the database with (using sqlalchemy) 
1. the sql, which are seperate files which are needed to generate the needed tables to query from, these only need to be run once


## Installation

### Python version
This project uses python3.8 as basis.
It's handy to create a virtual environment for this project.
```
python -m venv env
or
python3.8 -m venv env
```

then activate the virtual environment
```
source /env/bin/activate
```

then, to install all dependencies this project uses:

```
pip install -r requirements.txt
```

### Database
The database type being used is an PostgreSQL database based on version 13.5. a local installation or external database connection is required for the scripts to work properly.
 <br/>
The data is stored in a local database, credentials can be supplied through ``` .env ``` file or loading directly into your environment with this format: 
<br/>

```
user= """your username here"""
host="""your host here"""
port="""your port here"""
dbname="""your database name here"""
```
<br/>

The source data is gathered from the [3D BAG PostgreSQL datadump](https://3dbag.nl/nl/download) 
<br/>
After the data is loaded into a database, the needed tables need to be generated from either the sqlachemy table definitions specified in the /models directory,
or created manually using the scripts in the /sql directory.


## Running the calculation script
Run the gathering script using the CLI, for example:
```
python -m src.cli --bag_id=0867100000018868
```

## Running the visualisation 
TODO


