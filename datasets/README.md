# Project Datasets

## Syndromic Data
[Michigan Syndromic Surveillance System (MSSS)](https://www.michigan.gov/mdhhs/keep-mi-healthy/communicablediseases/mdss/michigan-syndromic-surveillance-system)

Syndromic data include visits to emergency departments (ED) and urgent care with chief complaints (CC) related to ILI. ILI-related CCs are defined as visits with ILI keywords *flu, fever, cough,* or *sore throat* in the most up-to-date case notes, without containing the following keywords: *stomach shot imm tamiflu vaccin inject mist reflux fluid fluids flutter fluttering fluctuating fluctuations flushed flush fluent*

Data are reported in aggregate, with total daily ILI-related visits accross all MSSS-participating facilities in Kent County, MI. 

---

## Incidence Data
[Michigan Disease Surveillance System (MDSS)](https://www.michigan.gov/mdhhs/keep-mi-healthy/communicablediseases/mdss/michigan-disease-surveillance-system-background)

ILI case definition: fever over 100 °F alongside sore throat, cough, or both, with no other explanation of illness besides ILI

MDSS ILI cases reflect clinician-diagnosed and/or laboratory-confirmed cases. Sentinel physicians and laboratories participate with the State of Michigan Outpatient Influenza-Like Illness Surveillance Network (ILINet) to report confirmed cases of ILI. 

---

## Online Search Trends
[Google Extended Trends for Health (GETH)](https://doi.org/10.1016/j.simpa.2021.100060)

Influenza-related internet search trends were acquired through the Google Extended Trends (GET) Application Programming Interface (API). The data represents the raw probability (x10^7) of a specific term being searched during a specified time and within a Designated Market Area (DMA), from a representative sample of all searches during that time period in that location. 

Google category code 419 filters for health-related searches 

DMA US-MI-563 represents Kent County, MI. 

*More info about GETH [here](https://doi.org/10.1016/j.simpa.2021.100060) and [here](https://www.mdpi.com/1660-4601/19/22/15396#app1-ijerph-19-15396). Go [here](https://support.google.com/trends/contact/trends_api) to request private access. Go [here](https://docs.google.com/forms/d/e/1FAIpQLSfDhe_gg28tgeEttsSAPCmdO4U0wbqorVBG4Azr46IowGkCtA/viewform) to view Google's private API access TOS*

---

## Weather Data
[National Centers for Environmental Information (NCEI)](https://www.ncei.noaa.gov/cdo-web/)

 Daily measurements for observed temperatures, daily precipitation/snowfall, and average windspeed are collected from the NCEI Access Data Service API, which provides programmatic access to the NOAA Global Historical Climate Network – Daily dataset. 
 
 The station id was GHCND:USW00094860, representing the Grand Rapids Gerald R. Ford International Airport station. 

 ---

## Air Quality Data
[Environmental Protection Agency (EPA) Air Quality System (AQS)](https://www.epa.gov/aqs)

Daily measurements for AQI, carbon monoxide, ozone, PM10, and PM2.5 from EPA's Air Quality System, which is a repository for daily air measurements as mandated by The Clean Air Act. 

Days exposed to moderate or bad air quality were recorded according to EPA’s AQI categories as follows: 

    0-50     -   Good
    51-100   -   Moderate
    101-150  -   Unhealthy for Sensitive Groups
    151-200  -   Unhealthy
    201-300  -   Very Unhealthy
    301-500  -   Hazardous for Health



