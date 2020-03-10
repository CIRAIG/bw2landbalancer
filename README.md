# bw2landbalancer

bw2landbalancer is a Python library used to create balanced land transformation samples to override unbalanced sample.

Unbalanced samples arise when land transformation exchanges are independently sampled. 
``bw2landbalancer`` rescales certain land transformation exchanges to ensure that the ratio of 
land transformation *from* exchanges and land transformation *to* exchanges is conserved. It is based on the 
[Brightway2 LCA framework](https://brightwaylca.org/), and is meant to be used with 
[presamples](https://presamples.readthedocs.io/en/latest/).
 
It was developped with ecoinvent in mind, though the modifications required to make it useful for other databases would be minimal.
Currently, elementary flows (biosphere exchanges in Brightway2) are identified as land transformation inputs or outputs 
based on the patterns "Transformation, from" and "Transformation, to", respectively.
Other patterns can be added.    

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bw2landbalancer:

```bash
pip install bw2landbalancer
```

or use conda: 
```bash
conda install --channel pascallesage bw2landbalancer
```

## Usage

```python
from bw2landbalancer import DatabaseLandBalancer
from brightway2 import projects

projects.set_current("my project")

dlb = DatabaseLandBalancer(
    database_name="ecoinvent_cutoff", #name the LCI db was given on import
)
```
Note: This is where one could add additional patters to identify land transformation exchanges, via the `land_from_patterns` and `land_to_patterns` (lists of strings).

```python
# Generate samples, and format as matrix_data for use in presamples
dlb.add_samples_for_all_acts(iterations=1000)
```
0% [##############################] 100% | ETA: 00:00:00
Total time elapsed: 00:18:11

```python
# Create presamples package
dlb.create_presamples(
    name='some name', 
    dirpath=some/path, 
    id_='some id',
    seed='sequential', #or None, or int
    )
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Acknowledgment
Special thanks to Quantis US for having funded the early iterations of this work. 
