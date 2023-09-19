import click
from src.bag_extractor.db_handler import BagCollector
from src.image_extractor.image_collector import ImageCollector
from src.polygon_calculator.surface_calculator import SurfaceCalculator
from src.model_generator.cityjson_generator import CityJSONGenerator

cli_group = click.Group()


@cli_group.command()
@click.option("-bag_id", "--bag_building_id", type=str, required=False, default=None)
def collect_and_generate_cityjson(bag_building_id: str):
    """
    Runs the calculation process

    big bad building example: 0867100000010575
    mediocre building example: 0867100000011372
    small, cubic building example: 0867100000025874
    L-shape building example: 0867100000018868
    spaces rotterdam (office): 0518100000204025
    corner building (simple): 0855100000281914
    school: 0599100000690512

    """

    bag_collector = BagCollector()
    surface_calculator = SurfaceCalculator()
    image_collector = ImageCollector()
    model_generator = CityJSONGenerator()

    # collect the selected bag data and polygons
    building = bag_collector.collect_building(bag_building_id)
    outer_wall_bboxes, roof_bboxes = surface_calculator.calculate_surface_bounding_boxes(building)
    panoramas, streetview_images, aerial_images = image_collector.collect_images(outer_wall_bboxes, roof_bboxes)
    cropped_roof_images = surface_calculator.process_roof_images(building=building, images=aerial_images)

    bag_collector.store_streetview(panoramas, streetview_images)
    bag_collector.store_aerial(cropped_roof_images=cropped_roof_images)

    # still busy with trying to model, WIP.
    cm = model_generator.generate(
        building=building,
        textures_enabled=True
    )

    model_generator.save(
        building=building,
        images=streetview_images + cropped_roof_images,
        cm=cm,
        filename='prototype_portfolio'
    )


@cli_group.command()
@click.option("-bag_id", "--bag_building_id", type=str, required=False, default=None)
def generate_cityjson_from_db(bag_building_id: str):

    bag_collector = BagCollector()
    model_generator = CityJSONGenerator()

    building = bag_collector.collect_building(bag_building_id)
    streetview_images, cropped_roof_images = bag_collector.collect_images(bag_building_id)
    cm = model_generator.generate(
        building=building,
        textures_enabled=True
    )

    model_generator.save(
        building=building,
        images=streetview_images + cropped_roof_images,
        cm=cm,
        filename='prototype_portfolio'
    )

if __name__ == "__main__":
    cli_group()
