# Compiler

This project was created in January 2024 for the **Formal Languages and Translation Techniques** course, which is a part of **Algorithmic Computer Science** study programme at Wrocław University of Science and Technology.

This project took part in the competition for the best compiler (i.e., the one creating the fastest and shortest programs), which was held among all 91 students attending the course. It was ranked the **4th** best solution and was therefore graded with the highest possible mark of **5.5**.

Specification for the project can be found in the file [specification.pdf](specification.pdf) (in polish).

## Running the compiler
The project is stored in the [compiler](compiler) folder.
It can be run by using the following command:

```
python3 compiler.py <input file> <output file>
```

#### Prerequisites

* python 3.8.10
* sly (`pip install sly`)

## Running the virtual machine
The files outputted by the compiler can be tested on the virtual machine provided for the task by the professor.
It is stored in the [virtual_machine](virtual_machine) folder.

To build the virtual machine, use `make vm`. Then run it with the following command:

```
./run-vm <input-file-path>
```

You can also run the version of the machine that uses the libcln-dev 1.3.6 library.
For that, run the machine with the following command:
```
./cln-run-vm <input-file-path>
```

#### Prerequisites

* bison (GNU Bison) 3.8.2
* flex 2.6.4
* GNU Make 4.3
* g++ 11.4.0
* libcln-dev 1.3.6

## Examples for testing
Files for testing the compiler are provided in the subfolders of the [examples](examples) folder.
