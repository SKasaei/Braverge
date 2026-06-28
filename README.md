
<p align="center">
  <img width="900" height="250" src="https://github.com/user-attachments/assets/91cb5c8d-325c-43f5-9467-0d89f9e2a2c1">
</p>

<p align="center">

**Branch boldly! Version intelligently! Merge cleanly!**

*A Collaborative Model Version Management Framework for Model-Based Systems Engineering*

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Research%20Prototype-success.svg)
![Platform](https://img.shields.io/badge/Platform-Cross--Platform-blue.svg)

</p>

---

## Overview

Braverge is a collaborative framework for **model version management** in **Model-Based Systems Engineering (MBSE)** and **Model-Driven Engineering (MDE)**. It provides integrated support for **model versioning**, **branching**, **merging**, **conflict management**, and **fine-grained access control**, enabling distributed teams to collaboratively evolve engineering models while preserving consistency and traceability.

Unlike traditional version control systems that operate on textual model serializations (e.g., XMI), Braverge performs model-aware operations based on the structural representation of models. The framework is independent of specific modeling tools, repositories, and metamodels, making it suitable for heterogeneous engineering environments.

This repository accompanies the journal manuscript:

> **Coming Soon-International Journal on Software and Systems Modeling (SoSyM)**

---

## Key Features

* 🌱 **Model Version Management**

  * Version history
  * Model snapshots
  * Change tracking
  * Metadata management

* 🌿 **Branch Management**

  * Hierarchical branching
  * Permanent and temporary branches
  * Branch synchronization
  * Branch lifecycle management

* 🔀 **Bidirectional Three-Way Merge**

  * Update operations
  * Merge operations
  * Automatic merge
  * Semi-automatic conflict resolution

* ⚠ **Conflict Management**

  * Structure-aware conflict detection
  * Conflict classification
  * Manual conflict resolution support

* 🔐 **Fine-Grained Access Control**

  * Branch-level permissions
  * View-based access control
  * Stakeholder-oriented collaboration

* 👥 **Multi-View Collaboration**

  * Concern-oriented model views
  * Synchronized editing
  * Collaborative model development

* 🔍 **Structure-Aware Model Comparison**

  * Semantic differencing
  * Structural comparison
  * Change analysis

* 📄 **Change Representation**

  * Braverge Change Operation Syntax (BCOS)
  * Branch Metadata Schema (BMS)

---

## Framework Architecture

The framework follows a modular layered architecture consisting of collaboration, version management, branching, merge, conflict management, access control, metadata management, and repository services.

---

## Repository Structure

```text
braverge/
│
├── docs/                  # Documentation
├── source/                # Framework implementation
├── examples/              # Example modeling projects
├── experiments/           # Experimental evaluation
├── datasets/              # Benchmark datasets
├── tests/                 # Test cases
├── figures/               # Paper figures
├── paper/                 # Supplementary material
│
├── README.md
├── LICENSE
└── CITATION.cff
```

---

## System Requirements

* Java 17 or newer
* Eclipse Modeling Framework (EMF)
* Eclipse IDE (recommended)
* Maven or Gradle
* Git

---

## Installation

Clone the repository

```bash
git clone https://github.com/<username>/braverge.git
```

Navigate to the project directory

```bash
cd braverge
```

Build the project

```bash
mvn clean install
```

or

```bash
gradle build
```

Detailed installation instructions are available in the `docs/` directory.

---

## Quick Start

A typical workflow consists of the following steps:

1. Import one of the example projects.
2. Create a feature branch.
3. Modify the model.
4. Commit the changes.
5. Synchronize with the parent branch.
6. Resolve any detected conflicts.
7. Merge the branch back into the main development branch.

Example projects are available in:

```text
examples/
```

---

## Reproducing the Paper

This repository contains the artifacts used in the accompanying journal submission.

| Paper Component          | Repository Location |
| ------------------------ | ------------------- |
| Framework Implementation | `source/`           |
| Architecture             | `docs/`             |
| Example Projects         | `examples/`         |
| Benchmark Models         | `datasets/`         |
| Experimental Evaluation  | `experiments/`      |
| Test Cases               | `tests/`            |
| Supplementary Material   | `paper/`            |

Additional documentation for reproducing the experimental evaluation is provided in the `experiments/` directory.

---

## Documentation

Documentation included in this repository:

* User Guide
* Installation Guide
* Developer Guide
* Framework Architecture
* API Documentation
* Example Projects
* Experimental Reproducibility Guide

---

## Example Applications

Braverge is applicable to collaborative modeling in domains including:

* Model-Based Systems Engineering (MBSE)
* Model-Driven Engineering (MDE)
* Cyber-Physical Systems
* Embedded Systems
* Industrial Automation
* Robotics
* Automotive Systems
* Aerospace Systems
* Digital Twins
* Smart Manufacturing

---

## Citation

If you use Braverge in your research, please cite the accompanying publication.

```bibtex
@article{-,
  title   = {-},
  author  = {-},
  journal = {-},
  year    = {-}
}
```

---

## Contributing

Contributions, bug reports, and feature requests are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

Please ensure that new contributions include appropriate documentation and tests.

---

## Contact

**Mohammad-Sajad Kasaei**

📧 [smskasaei@gmail.com](mailto:smskasaei@gmail.com)

---

## License

This project is distributed under the **MIT License**.

See the `LICENSE` file for additional information.

---

## Acknowledgements

Braverge has been developed as part of ongoing research on collaborative model version management for Model-Based Systems Engineering and Model-Driven Engineering. We thank all collaborators and reviewers for their valuable feedback throughout the development of the framework.
