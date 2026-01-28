# (C) Copyright 1996- ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


# To run this code you need to use pip install thermofeel
# import statements
import datetime

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset  # , date2num, num2date

from earthkit.meteo.solar import (
    cos_solar_zenith_angle,
    cos_solar_zenith_angle_integrated,
)

from thermofeel import (
    approximate_dsrp,
    calculate_apparent_temperature,
    calculate_bgt,
    calculate_heat_index_adjusted,
    calculate_heat_index_simplified,
    calculate_humidex,
    calculate_mean_radiant_temperature,
    calculate_mrt_from_bgt,
    calculate_normal_effective_temperature,
    calculate_relative_humidity_percent,
    calculate_saturation_vapour_pressure,
    calculate_utci,
    calculate_wbgt,
    calculate_wbgt_simple,
    calculate_wbt,
    calculate_wind_chill,
)

# read in two netcdf files containing all the variables
# to calculate the thermal indexes
my_example_nc_file2 = "radiation.nc"
fh2 = Dataset(my_example_nc_file2, mode="r")
lons = fh2.variables["longitude"][:]
lats = fh2.variables["latitude"][:]
ssrd = fh2.variables["ssrd"][0]
ssr = fh2.variables["ssr"][0]
fdir = fh2.variables["fdir"][0]
strd = fh2.variables["strd"][0]
strr = fh2.variables["str"][0]

lon_mg, lat_mg = np.meshgrid(lons, lats)

my_example_nc_file3 = "utcicomponents1.nc"
fh3 = Dataset(my_example_nc_file3, mode="r")
windspeed = np.sqrt(fh3.variables["u10"][0] ** 2 + fh3.variables["v10"][0] ** 2)
t2m = fh3.variables["t2m"][0]
td = fh3.variables["d2m"][0]

# calculate all indexes from thermofeel
rhp = calculate_relative_humidity_percent(t2_k=t2m, td_k=td)
svp = calculate_saturation_vapour_pressure(t2_k=t2m)
cosszainstant = cos_solar_zenith_angle(
    datetime.datetime(2020, 6, 8, 6), lat_mg, lon_mg
)
cosszaintegrated = cos_solar_zenith_angle_integrated(
    datetime.datetime(2020, 6, 8, 0), datetime.datetime(2020, 6, 8, 6), lat_mg, lon_mg
)

approx_dsrp = approximate_dsrp(fdir=fdir, cossza=cosszainstant)

mrtinstant = calculate_mean_radiant_temperature(
    ssrd=ssrd,
    ssr=ssr,
    dsrp=approx_dsrp,
    fdir=fdir,
    strd=strd,
    strr=strr,
    cossza=cosszainstant,
)
approx_dsrp_integrated = approximate_dsrp(fdir=fdir, cossza=cosszaintegrated)
mrtintegrate = calculate_mean_radiant_temperature(
    ssrd=ssrd, ssr=ssr, dsrp=approx_dsrp_integrated, strd=strd, fdir=fdir, strr=strr, cossza=cosszaintegrated
)
utci = calculate_utci(t2_k=t2m, va=windspeed, mrt=mrtintegrate, td_k=td)
wbgts = calculate_wbgt_simple(t2_k=t2m, rh=rhp)
wbt = calculate_wbt(t2_k=t2m, rh=rhp)
bgt = calculate_bgt(t2_k=t2m, mrt=mrtintegrate, va=windspeed)
wbgt = calculate_wbgt(t2_k=t2m, mrt=mrtintegrate, va=windspeed, td_k=td)
mrtbg = calculate_mrt_from_bgt(t2_k=t2m, bgt_k=bgt, va=windspeed)
humidex = calculate_humidex(t2_k=t2m, td_k=td)
net = calculate_normal_effective_temperature(t2_k=t2m, va=windspeed, rh=rhp)
aptmp = calculate_apparent_temperature(t2_k=t2m, va=windspeed, rh=rhp)
windchill = calculate_wind_chill(t2_k=t2m, va=windspeed)
hisimple = calculate_heat_index_simplified(t2_k=t2m, rh=rhp)
hia = calculate_heat_index_adjusted(t2_k=t2m, td_k=td)

# to plot a single figure the example is for humidex index
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
filled_c = plt.pcolormesh(
    lon_mg, lat_mg, (humidex), transform=ccrs.PlateCarree(), cmap="RdBu_r"
)
fig.colorbar(filled_c, orientation="horizontal")
plt.show()
