# Flood Impacts Workflow
The flood impacts workflow combines the City Catchment Analysis Tool (CityCAT) and a flood impacts calculator which 
assesses damages to buildings caused by flooding. Expected annual damages can be calculated by running the workflow for 
multiple event return periods. Future scenarios can be simulated using event uplifts and adaptation measures reviewed. 
The workflow is available on DAFNI here. The source code is available on GitHub for the CityCAT and Flood Impacts models.

## CityCAT hydrodynamic simulation
The CityCAT DAFNI model wraps the Windows binary executable CityCAT.exe in a Python script which pre-processes input 
data and post-processes output data. The Windows emulator Wine is used to run CityCAT on Linux. The source code for 
CityCAT itself is not publicly available, however the code used to create the Docker image can be accessed 
[here](https://github.com/OpenCLIM/citycat-dafni), along with further documentation. 

### Input Data
The following are default datasets and can be replaced if required.

#### OS Terrain 5
The DEM is extracted from OS Terrain 5 which is a corrected digital surface model of the UK with 5m resolution. The 
dataset was created using a combination of photogrammetry and topographic survey and is updated regularly. This data 
is licenced for research only.

#### OS MasterMap
Polygons from OS MasterMap are used to represent buildings and green spaces. MasterMap is the most comprehensive is the 
most detailed and up-to-date view of Britain’s landscape. This data is licenced for research only.

#### Urban Development Model (UDM) Urban Fabric
Optionally, UDM can be integrated into the workflow. If this is case, then the buildings from the UDM urban fabric layer 
are combined with the buildings from OS MasterMap to create a combined future projection. 

#### Discharge boundary condition
Optionally, discharge can be used as an input boundary condition. If this is provided, then a file containing a polygon 
that overlaps with domain cell boundaries is required. Discharge is routed into the domain at these overlapping cell 
boundaries. The discharge is distributed uniformly over the specified duration and gets multiplied by the number of 
cells intersected.

#### FUTURE-DRAINAGE Rainfall Event Uplifts
Rainfall depths for a range of return periods, durations and time periods are provided by FUTURE-DRAINAGE. The estimates 
are based on 2.2 km hourly precipitation data from UKCP18 for RCP 8.5. Baseline rainfall depths are provided describing 
the period 1981-2000 in the ReturnLevel.<year> field. Percentage uplifts are available for two future horizons, 2050 and 
2070. The values are provided for points on a 5km grid covering the UK.

Table 1 - Example rows from a FUTURE-DRAINAGE CSV file for the 100-year return period

| easting | northing | ReturnLevel.100 | Uplift_50 | Uplift_95 |
| --- | --- | --- | --- | --- |
| 92500 | 12500 | 39.1 | 15 | 40 |
| 167500 | 12500 | 38.9 | 15 | 40 |
| 172500 | 12500 | 39.1 | 15 | 40 |

### Configuration

#### Domain
The domain can either be supplied as a boundary (Shapefile or GeoPackage) or the coordinates of a central point and the 
size in km. The coordinates and size combination are used by default. The size represents the length of each side of a 
square with centroid at the specified coordinates. The polygon, described either by the size and coordinates or by the 
boundary, is used to clip OS Terrain 5 to create a DEM which defines the domain. Any DEM cells falling within a building 
polygon are removed from the domain. Water is prevented from flowing into these removed areas using closed cell boundary 
conditions. 

#### Rainfall event
Two rainfall modes are available. If the model is run in rainfall mode, the value for total depth is used to define the 
event. If the model is run in return period mode, the total depth is extracted from the FUTURE-DRAINAGE dataset based on 
the specified return period and event duration. If the time horizon is set to anything other than baseline with the 
rainfall model set to return period, the total depth is uplifted by the corresponding percentage from the 
FUTURE-DRAINAGE data. The event is then shaped using the specified duration and a storm profile based on the FEH summer 
profile. If a post-event of greater than zero is provided, the simulation will continue to run following the event for 
that length of time.

#### Green areas
Three modes are available for modelling green areas. If the parameter is set to permeable, the entire domain will be 
assumed to be permeable. If it is set to impermeable, the entire domain is assumed to be impermeable. If the polygons 
mode is selected, any cells falling within the provided green areas polygons are designated as permeable. Permeable 
areas allow infiltration to take place.

#### Green rooves
A parameter for the depth of water stored on every building roof can be provided. By default, this value is zero. There 
is no existing functionality to be able to specify a different storage value for different buildings, but this feature 
is in development. 

### Output
The CityCAT model outputs four GeoTIFF files describing maximum depth, maximum depth with gaps interpolated, maximum 
velocity and maximum velocity-depth product. The maximum depth is also plotted in a PNG file (Figure 1). The depths 
and velocities from all timesteps are stored in a netCDF file and archived to a ZIP file.
 
![Figure 1](/docs/img/figure-1.png)
Figure 1. Maximum water depth for the 100-year flood event in Glasgow, 2070.

## Flood impacts (Calculating damages)
The flood impacts DAFNI model uses the outputs from CityCAT to calculate flood damage to buildings. Alternative 
hydrodynamic models could be used if the output data matches the format. Damages from multiple events can be used 
to calculate expected annual damage. All code for this model is open source and can be accessed 
[here](https://github.com/OpenCLIM/flood-impacts-dafni), along with further documentation. 

### Input Data
The following are default datasets and can be replaced if required.

#### CityCAT Results
The maximum depth and velocity-depth product CityCAT output files are used to calculate the maximum depth and 
velocity-depth product surrounding each building.

#### OS MasterMap (including NISMOD classifications)
Buildings are extracted from OS MasterMap and buffered by 5m to calculate maximum depth and velocity-depth product from 
the CityCAT results. The flooded perimeter is also calculated for each building. The building classifications are used 
to decide which depth-damage curve to use.

#### TOID-UPRN Lookup
Unique Property Reference Numbers are used to identify individual properties of which there can be multiple within a 
given building. If this lookup table is provided, outputs will be given for each UPRN as well as each TOID.

#### Depth-damage curves
Two depth-damage curves are required, describing the relationship between depth and damage for residential and 
non-residential properties. These can be user defined. The JRC curves for the United Kingdom describing damage to 
contents only, are used by default.

### Configuration

#### Threshold
Building depths are reduced by a given threshold before calculating damages using the depth-damage curves. This is to 
account for the height of the floor above ground level. A value of 0.3m is used by default. The threshold is also used 
when calculating flooded perimeters.

### Output
The flood impacts model outputs a single CSV file containing depths, damages, velocity-depth products, and flooded 
perimeters for either each building (TOID) or property (UPRN).

Table 2 - Example output CSV from the flood impacts model

| toid | depth | damage | vd_product | flooded_perimeter |
| --- | --- | --- | --- | --- |
| osgb1000000313425904 | 0.019 | 4 | 0.013 | 14 |
| osgb1000040429529 | 0.268 | 12910 | 0.019 | 33 |
| osgb1000002038581673 | 0.072 | 1816 | 0.027 | 10 |

## Calculating Expected Annual Damages
To generate expected annual damage, the workflow needs to be run multiple times for different return periods. The 
calculation of EAD must then be done away from DAFNI as multiple outputs are required. A threshold flooded perimeter 
can be used before calculating EAD to filter out buildings from the analysis. The recommended threshold for surface 
water flooding in Britain is 50% but other values may be more appropriate for specific locations. Once this threshold 
has been applied, EAD can be calculated as follows.

The first step is to calculate the probability of non-exceedance for each return period, given by e^((-1)/T) where T is 
the return period in years. Then, the probability of each return period is calculated by taking the difference between 
each non-exceedance probability and the non-exceedance probability of the next shortest return period. The probability 
of the shortest return period is equivalent to the non-exceedance probability of this return period. The difference 
between 1 and the total of all probabilities is added to the probability of the longest return period. An example of 
the calculation is shown in Table 1 and Equation 1.

Table 3 - Example return period damages and probabilities
| Return Period | Band | Damage| Probability of non-exceedance | Probability |
| --- | --- | --- | --- | --- |
| 2	| <2 | 52698 | 0.606531	| 0.606531 |
| 30 | 2-30	| 942618.5 | 0.967216 | 0.360685 |
| 100 | >30	| 1583538 | 0.99005	| 0.032784 |

Equation 1 - Expected Annual Damage calculation

`expected annual damage = ∑(damage × probability) = £423,866`