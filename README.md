
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

## Tutorials

To help users get started with Braverge, a collection of video tutorials is available. The playlist demonstrates the main features of the framework, including repository creation, model versioning, branching, merging, conflict management, and collaborative workflows.

📺 **Official Braverge Video Tutorials**

[Braverge Official YouTube Playlist](https://www.youtube.com/playlist?list=PLgVoclgulFnQ039tyl5yltIGf_gru7r4C&utm_source=chatgpt.com)

The playlist includes tutorials covering:

* Installing and launching Braverge
* Creating and managing repositories
* Importing engineering models
* Creating and managing branches
* Comparing model versions
* Merging branches
* Resolving conflicts
* Managing collaborative projects
* Using advanced Braverge features

New tutorials will be added as the framework evolves.
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
├── experiments/           # Empirical and Experimental evaluation
│
├── README.md
├── LICENSE
└── CITATION.cff
```

---

## System Requirements

To run Braverge, the following software is required:

* Python **3.10** or later (Python 3.11 recommended)
* Git (for cloning the repository)
* Graphviz (required for graph visualization)
* Windows 10/11, Linux, or macOS

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/SKasaei/Braverge.git
```

### 2. Navigate to the project directory

```bash
cd Braverge
```

### 3. Install the required Python packages

```bash
pip install -r requirements.txt
```

### 4. Run Braverge

```bash
python main.py
```

The Braverge graphical user interface will launch, allowing you to create or open a repository and begin collaborative model version management.


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
