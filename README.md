# Compiler

This project was created in January 2024 for the **Formal Languages and Translation Techniques** course which is a part of **Algorithmic Computer Science** study programme in Wrocław University of Science and Technology.

It took part in the competition between all 91 students participating in the course for the best compiler, i. e. the one creating the fastest and shortest programs. This project was ranked **4th** best solution and was therefore graded with the highest possible mark of **5.5**.

Specification for the project can be find in the file [specification.pdf](specification.pdf) (in polish).

## Running the compiler
The project is stored in the [compiler](compiler) folder.
It can be run by using command:

```
python3 compiler.py <input file> <output file>
```

#### Prerequisites

* python 3.8.10
* sly (`pip install sly`)

## Running the virtual machine
The files outputed by the compiler can be tested on the virtual machine provided for the task by the professor.
It is stored in the [virtual_machine](virtual_machine) folder.

To build the virtual machine use `make vm`. Then run it with command:

```
./run-vm <input-file-path>
```

You can also run the version of the machine which uses libcln-dev 1.3.6 library.
For that run the machine with command:
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
Files for testing the compiler are provided in the subfolders of the [test](test) folder.
