# dengo-templates
helper function to generate templates for hydro simulations

## Enzo-template
- Enzo template files are in the enzo-templates/templates
- the templates can be generated with Jinja2 with `generateEnzoTemplates.py`
- sample enzo parameter is `music_input.enzo`

## Outline of what `generateEnzoTemplates.py` does
1. Initialize an `Dengo` `ChemicalNetwork` object with all the reactions and rates
2. Based on the reactions and chemical cooling/ heating, the required scripts are generated from pre-written enzo templates files. (Currently it works with the particular commit: `8f75306d89476ed897228e39e604f4769add217b`. Checkout this particular commit for a working integration. We will work to incorporate it to more recent versions of Enzo).
3. The templates written based on `Dengo` are placed in `templatedir` 
4. They can then be placed in the directory `enzo-dev/src/enzo`

5. Dengo-enabled enzo can be built by `make dengo-yes grackle-no`, below shows the example snippit from `make show-config`. 
```
CONFIG_GRACKLE  [grackle-{yes,no}]                        : no
CONFIG_DENGO    [dengo-{yes,no}]                          : yes
```
6. Specify the paths to various libraries in respective `Make.mach.linux-gnu`, by default `Dengo` would fill them out automatically if the paths are specified already in the enviroment or in the `ChemicalNetwork` object.
```
LOCAL_DENGO_INSTALL = {{network._dengo_install_path}}
LOCAL_CVODE_INSTALL = {{network._cvode_path}}
LOCAL_SUITESPARSE_INSTALL = {{network._suitesparse_path}}
```
7. Now try making `enzo`! Make sure the `mpic++` is built with the same `gcc` you use to build `Dengo`

