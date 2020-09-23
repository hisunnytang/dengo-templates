from generateGamerTemplates import setup_primordial_network, write_from_templates
from jinja2 import Environment, BaseLoader
import os
import subprocess


def cloneDengoBranch(newName = None, gamerFork = "https://github.com/hisunnytang/gamer-fork"):
    cloneDengoBranch = f"git clone -b dengo {gamerFork}"
    if newName is not None:
        cloneDengoBranch += f" {newName}"

    if os.path.exists("./gamer"):
        print("Path exists")
    # clone the Dengo Branch
    out = subprocess.run(cloneDengoBranch, check=True)


def writeGamerTemplates(network = None, solver_name="dengo-primordial"):
    if network is None:
        network = setup_primordial_network()
    # write Gamer templates
    outfiledir = "autogen_gamer_templates"
    if not os.path.exists(outfiledir):
        os.mkdir(outfiledir)
    templatedir = "../gamer-templates/templates"
    write_from_templates(network, solver_name, searchpath=templatedir, outdir=outfiledir)


def appendIncludeFile(network, solver_name='dengo_primordial', gamer_dir="gamer-fork"):
    dengo_dir = f"{gamer_dir}/{solver_name}"
    GAMER_H_template = f"""\n#ifdef SUPPORT_DENGO\n#include "{solver_name}_solver.h"\n#endif\n"""

    FIELD_H_template = """\n// Dengo fields\n{%- for s in network.required_species | sort %}\nSET_GLOBAL( FieldIdx_t Idx_{{s.name}}, Idx_Undefined );\n{%- endfor %}\n\n"""

    def write_template_string(s):
        rtemplate = Environment(loader=BaseLoader()).from_string(s)
        template_vars = dict(network=network, solver_name=solver_name)
        return rtemplate.render(template_vars)

    gamerH_ = write_template_string(GAMER_H_template)
    fieldH_ = write_template_string(FIELD_H_template)

    with open(os.path.join(gamer_dir, "include", "GAMER.h"), 'r+') as f:
        contents = f.readlines()
        match_string = "#endif // #ifdef SUPPORT_GRACKLE"

        stringStart = gamerH_.split("\n")[0]
        if match_string in contents[-1]:
            contents.append(gamerH_)
        else:
            for idx, line in enumerate(contents):
                if match_string in line and stringStart not in contents[idx+1]:
                    contents.insert(idx+1, gamerH_)
                    break
        f.seek(0)
        f.writelines(contents)

    with open(os.path.join(gamer_dir, "include", "Field.h"), 'r+') as f:
        contents = f.readlines()
        match_string = "#ifdef SUPPORT_DENGO"

        stringStart = fieldH_.split("\n")[0]
        if match_string in contents[-1]:
            contents.append(fieldH_)
        else:
            for idx, line in enumerate(contents):
                if match_string in line and stringStart not in contents[idx+1]:
                    contents.insert(idx+1, fieldH_)
                    break
        f.seek(0)
        f.writelines(contents)

def writeDengoNetwork(network= None, gamerdir = None,solver_name="dengo_primordial", solver = "be_chem_solve"):
    # write our Dengo Chemistry solver
    # and compile it
    if network is None:
        network = setup_primordial_network()

    if gamerdir is None:
        gamerdir = "gamer-fork"
    outputdir = f"{gamerdir}/{solver_name}"

    if solver == 'be_chem_solve':
        network.write_solver(solver_name,
                             solver_template="be_chem_solve/rates_and_rate_tables",
                             ode_solver_source="BE_chem_solve.C",
                             output_dir = outputdir)
    elif solver == "sundials":
        network.write_solver(solver_name,
                             solver_template = "cv_omp/sundials_CVDls",
                             ode_solver_source = "initialize_cvode_solver.C",
                             output_dir = outputdir)

def moveGamerTemplates(template_dir='autogen_gamer_templates', gamer_dir='gamer-fork'):
    # files needed by Gamer
    files = ['src/Init/Init_Field.cpp', 'src/Makefile']
    out = subprocess.run("pwd")
    for f in files:
        fn = os.path.join(template_dir, f)
        out = subprocess.run(["ls", f"{template_dir}/include"], check=True)
        out = subprocess.run(["cp", f"{fn}", f"{gamer_dir}/{f}"], check=True)
    out = subprocess.run(["cp", "-r", f"{template_dir}/src/Dengo", f"{gamer_dir}/src/"], check=True)


def buildDengoSolver(dengo_dir):
    current_path = os.getcwd()
    NTHREADS = 40
    os.chdir(dengo_dir)
    with open("Makefile", 'r+') as f:
        lines =f.readlines()
        for i, l in enumerate(lines):
            if "-fopenmp" in l:
                lines[i] = f"OPTIONS += -fopenmp -DNTHREADS={NTHREADS}\n"
        f.seek(0)
        f.writelines(lines)

    out = subprocess.run(["make"], check=True)

    print(out.returncode)
    os.chdir(current_path)
    return

def buildGAMER(gamer_dir, gamerOption={}, use_grackle=False):
    # rewrite the Makefile based on the options
    current_path = os.getcwd()
    os.chdir(os.path.join(gamer_dir, "src"))

    print(current_path)

    gamerOptions = {}
    gamerOptions['SUPPORT_GRACKLE'] = use_grackle
    gamerOptions['SUPPORT_DENGO'  ] = not use_grackle

    simu_option_string = {f"SIMU_OPTION += -D{k}": v for k, v in gamerOptions.items()}

    with open("Makefile", "r+") as f:
        lines = f.readlines()
        for idx, content in enumerate(lines):
            for s in simu_option_string:
                if s in content:
                    if simu_option_string[s]:
                      lines[idx] = f"{s}\n"
                    else:
                      lines[idx] = f"#{s}\n"
        f.seek(0)
        f.writelines(lines)

    out = subprocess.run(["make", "clean"], check=True)
    out = subprocess.run(["make", "-j32"], check=True)
    os.chdir(current_path)

def runGAMERTestProblem(gamer_dir, simu_dir="playground"):

    current_path = os.getcwd()
    print(current_path)
    os.chdir(gamer_dir)
    if not os.path.exists(simu_dir):
        os.mkdir(simu_dir)
    os.chdir(simu_dir)
    print(os.getcwd())
    out = subprocess.run(["rm gamer"], shell=True)
    out = subprocess.run(["rm Record*"], shell=True)
    out = subprocess.run(["rm Data*"], shell=True)
    sampleInputs = os.path.join(current_path, "gamerInput/Input*")
    print(os.getcwd())
    print(sampleInputs)

    print(["cp",f"{sampleInputs}","."])
    out = subprocess.run([f"cp {sampleInputs} ."], shell=True, check=True)
    out = subprocess.run(["cp ../bin/gamer ."], shell=True, check=True)

    out = subprocess.run(["./gamer", "&>", "run.out"],
                         stdout = subprocess.PIPE,
                         stderr = subprocess.PIPE)
    #with open("run_gamer.out", 'w') as f:
    #    f.write(out.stdout.read())
    os.chdir(current_path)

def runGrackleGAMER(gamer_dir, simu_dir="playgroun_grackle"):
    buildGAMER         (gamer_dir, use_grackle=True)
    runGAMERTestProblem(gamer_dir, simu_dir)

def runDengoGAMER (network, gamer_dir,
                   solver_name  ='dengo_primordial',
                   solver_option='be_chem_solve',
                   simu_prefix="playground_dengo",
                   write_gamer_files = True):

    # write the Dengo Solver
    dengoDir = f"{gamer_dir}/{solver_name}"
    writeDengoNetwork(network, gamer_dir, solver_name, solver_option)
    buildDengoSolver(dengoDir)

    if write_gamer_files:
        # write the Gamer based on the network
        writeGamerTemplates(network, solver_name)
        # copy the Gamer templates to the Repo
        moveGamerTemplates(gamer_dir = gamer_dir)
        # append the include file
        # for the initiallized species index
        appendIncludeFile(network, gamer_dir = gamer_dir)
    # build GAMER
    buildGAMER(gamer_dir, use_grackle=False)
    runGAMERTestProblem(gamer_dir, simu_dir=f"{simu_prefix}_{solver_option}")


if __name__ == "__main__":

    # Parameters
    solver_name     = "dengo_primordial"
    solver_option   = "be_chem_solve" # "sundials"
    gamerRenameRepo = "gamer_dengo"
    # Environment Variables
    os.environ["HDF5_DIR"]           = "/home/kwoksun2/anaconda3"
    os.environ["CVODE_PATH"]         = "/home/kwoksun2/dengo-merge/cvode-3.1.0/instdir"
    os.environ["HDF5_PATH"]          = "/home/kwoksun2/anaconda3"
    os.environ["SUITESPARSE_PATH"]   = "/home/kwoksun2/dengo-merge/suitesparse"
    os.environ["DENGO_INSTALL_PATH"] = "/home/kwoksun2/dengo_install"
    os.environ["LIBTOOL"]            = "/usr/bin/libtool"

    gamer_dir = "gamer_dengo"
    #runGrackleGAMER(gamer_dir, simu_dir="playgroun_grackle")

    # build a chemical network
    network = setup_primordial_network()
    runDengoGAMER(network, gamer_dir, solver_option='sundials')
    #runDengoGAMER(network, gamer_dir, solver_option='be_chem_solve')
    #runGrackleGAMER(gamer_dir, simu_dir="playground_grackle")
