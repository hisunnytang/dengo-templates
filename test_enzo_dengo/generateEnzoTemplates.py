from dengo.chemical_network import \
        ChemicalNetwork, \
        reaction_registry, \
        cooling_registry
import dengo.primordial_rates
import dengo.primordial_cooling
from dengo.chemistry_constants import tiny, kboltz, mh, G
import os
import jinja2
import sys
import glob


def setup_primordial_network():
    """Initial a ChemicalNetwork object
       for primordial network 9-species model
    Return:
        primordial: ChemicalNetwork with primordial reactions and cooling
    """
    # this register all the rates specified in `primordial_rates.py`
    dengo.primordial_rates.setup_primordial()

    # initialize the chmical network object
    primordial = ChemicalNetwork()

    # add all the reactions
    primordial.add_reaction("k01")
    primordial.add_reaction("k02")
    primordial.add_reaction("k03")
    primordial.add_reaction("k04")
    primordial.add_reaction("k05")
    primordial.add_reaction("k06")
    primordial.add_reaction("k07")
    primordial.add_reaction("k08")
    primordial.add_reaction("k09")
    primordial.add_reaction("k10")
    primordial.add_reaction("k11")
    primordial.add_reaction("k12")
    primordial.add_reaction("k13")
    primordial.add_reaction("k14")
    primordial.add_reaction("k15")
    primordial.add_reaction("k16")
    primordial.add_reaction("k17")
    primordial.add_reaction("k18")
    primordial.add_reaction("k19")
    primordial.add_reaction("k21")
    primordial.add_reaction("k22")
    primordial.add_reaction("k23")

    primordial.add_cooling("brem")
    primordial.add_cooling("reHII")
    primordial.add_cooling("reHeIII")
    primordial.add_cooling("gloverabel08")
    primordial.add_cooling("ceHI")
    primordial.add_cooling("h2formation")
    primordial.add_cooling("reHeII2")
    primordial.add_cooling("reHeII1")
    primordial.add_cooling("ciHeIS")
    primordial.add_cooling("ceHeII")
    primordial.add_cooling("ciHI")
    primordial.add_cooling("ceHeI")
    primordial.add_cooling("gammah")
    primordial.add_cooling("ciHeI")
    primordial.add_cooling("ciHeII")
    primordial.add_cooling("cie_cooling")
    primordial.add_cooling("compton")

    # This defines the temperature range for the rate tables
    primordial.init_temperature((1e0, 1e8))

    #primordial.enforce_conservation = True
    #primordial.set_equilibrium_species("H2_2")

    return primordial



def write_from_templates(network, searchpath=".", outdir="."):
    """Helper Function to write required files given the ChemicalNetwork
    
    Parameters
    ----------
    network: 
        `ChemicalNetwork` object with desired reactions
    searchpath:
        the location of the desired hydro integration templates
    outdir:
        the directory in which the templates files would be saved
    
    Returns
    -------
    None
    

    """
    templateLoader = jinja2.FileSystemLoader(searchpath=searchpath)
    env = jinja2.Environment(extensions=['jinja2.ext.loopcontrols'], loader=templateLoader)

    template_vars = dict(network=network, solver_name='primordial')
    templateFiles = list(map(os.path.basename, glob.glob(os.path.join(searchpath, "*.template"))))
    for infile in templateFiles:
        template_inst = env.get_template(infile)
        solver_out = template_inst.render(**template_vars)

        outfile = infile.replace(".template", "")
        with open(os.path.join(outdir,outfile), 'w') as f:
           f.write(solver_out)



if __name__ == "__main__":
    network = setup_primordial_network()

    outfiledir = "autogen_enzo_templates"
    if not os.path.exists(outfiledir):
        os.mkdir(outfiledir)
    templatedir = "../enzo-templates/templates"

    write_from_templates(network, searchpath=templatedir, outdir=outfiledir)
