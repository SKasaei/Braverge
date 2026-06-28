<p align="center">
 <img width="900" height="250" src="https://github.com/user-attachments/assets/91cb5c8d-325c-43f5-9467-0d89f9e2a2c1">
</p>

<p align="center">

**Branch boldly! Version intelligently! Merge cleanly!**

*A Collaborative Framework for Model Version Management in Model-Based Systems Engineering*

</p>

<p align="center">

![GitHub release](https://img.shields.io/github/v/release/USERNAME/braverge?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Java](https://img.shields.io/badge/Java-17+-orange?style=for-the-badge)
![Platform](https://img.shields.io/badge/platform-Eclipse%20EMF-blue?style=for-the-badge)

</p>

---

## Overview

**Braverge** is a collaborative model version management framework designed for **Model-Based Systems Engineering (MBSE)** and **Model-Driven Engineering (MDE)**. It enables engineering teams to collaboratively develop, evolve, and maintain software and system models through integrated support for model versioning, branching, merging, conflict management, and access control.

Unlike conventional version control systems that operate on textual representations of models (e.g., XMI), Braverge manages models at the structural level, preserving their semantics throughout the evolution process. The framework is independent of specific modeling tools, repositories, and metamodels, making it suitable for heterogeneous engineering environments.

Braverge has been developed to support collaborative engineering processes involving distributed teams, multiple stakeholders, and concurrent model evolution while maintaining consistency, traceability, and interoperability.

---

# Key Features

## 🌱 Model Version Management

Maintain complete histories of model evolution with version metadata, timestamps, authorship, and traceability information.

* Complete version history
* Version metadata
* Model snapshots
* Change tracking
* Version comparison

---

## 🌿 Branch Management

Support parallel model development through lightweight branches.

* Permanent and temporary branches
* Hierarchical branch organization
* Branch lifecycle management
* Branch synchronization
* Branch metadata

---

## 🔀 Intelligent Model Merging

Braverge provides bidirectional three-way merge operations supporting both:

* **Update** (integrating changes from parent branches)
* **Merge** (integrating completed work into parent branches)

Features include:

* Automatic merging
* Semi-automatic conflict resolution
* Manual conflict handling
* Merge previews
* Merge history

---

## ⚠ Conflict Management

The framework detects and manages model conflicts using structure-aware analysis.

Supported conflict categories include:

* Element addition conflicts
* Element deletion conflicts
* Update conflicts
* Move conflicts
* Reference conflicts
* Attribute conflicts
* Cross-reference inconsistencies
* Composite conflicts

---

## 🔐 Fine-Grained Access Control

Braverge introduces a dual-layer security mechanism.

### Branch-level permissions

* Owner
* Administrator
* Developer
* Reviewer
* Guest

### View-level permissions

Stakeholders can access only the model views relevant to their responsibilities, reducing complexity while protecting sensitive model information.

---

## 👥 Multi-View Collaboration

Collaborative engineering often requires different stakeholders to work on different aspects of a system.

Braverge supports synchronized model views that enable:

* Discipline-specific modeling
* Concern separation
* Reduced cognitive complexity
* Collaborative editing
* View synchronization

---

## 🔍 Structure-Aware Model Comparison

Instead of comparing text files, Braverge compares model structures.

Comparison considers:

* Elements
* Attributes
* References
* Hierarchies
* Relationships
* Structural modifications

This enables significantly more meaningful differencing and merging than conventional text-based version control systems.

---

## 📝 Change Operation Representation

Braverge introduces the **Braverge Change Operation Syntax (BCOS)** for representing model modifications in a structured and implementation-independent format.

BCOS enables:

* Model evolution tracking
* Version reconstruction
* Merge support
* Conflict analysis
* History inspection

---

## 📚 Branch Metadata Schema

Branch information is managed using the **Branch Metadata Schema (BMS)**.

The schema maintains:

* Branch identifiers
* Parent-child relationships
* Creation history
* Authors
* Permissions
* Status
* Merge history
* Branch lifecycle information

---

# Framework Architecture

Braverge follows a layered architecture separating collaborative concerns from version management mechanisms.

The framework consists of several major components:

* Collaboration Layer
* Branch Management
* Version Management
* Merge Engine
* Conflict Management
* Access Control
* Multi-View Manager
* Metadata Management
* Repository Layer

This modular architecture enables extensibility while remaining independent of modeling technologies and repositories.

---

# Typical Workflow

A typical collaborative development process consists of:

1. Create a project.
2. Initialize the main branch.
3. Create feature branches.
4. Develop models collaboratively.
5. Commit model changes.
6. Synchronize branches.
7. Resolve merge conflicts.
8. Merge completed branches.
9. Release stable versions.

---

# Repository Structure

```
braverge/
│
├── docs/
│   ├── architecture/
│   ├── user-guide/
│   ├── developer-guide/
│   └── api/
│
├── source/
│   ├── backend/
│   ├── frontend/
│   ├── services/
│   └── utilities/
│
├── examples/
│
├── experiments/
│   ├── benchmark/
│   ├── empirical-study/
│   └── evaluation/
│
├── datasets/
│
├── tests/
│
├── figures/
│
├── paper/
│
└── README.md
```

---

# Research Contributions

Braverge introduces several research contributions to collaborative model management:

* Unified collaborative model version management framework
* Comparison-based model versioning approach
* Branch Metadata Schema (BMS)
* Braverge Change Operation Syntax (BCOS)
* Hierarchical branch management
* Fine-grained branch and view access control
* Bidirectional three-way model merging
* Comprehensive conflict management framework
* Repository-independent architecture
* Tool-independent collaborative modeling infrastructure

---

# Applications

Braverge is suitable for numerous engineering domains including:

* Model-Based Systems Engineering (MBSE)
* Model-Driven Engineering (MDE)
* Software Architecture Modeling
* Automotive Systems
* Aerospace Engineering
* Robotics
* Industrial Automation
* Digital Twins
* Cyber-Physical Systems
* Smart Manufacturing
* Embedded Systems
* Internet of Things (IoT)

---

# Installation

Clone the repository

```bash
git clone https://github.com/USERNAME/braverge.git
```

Move into the project directory

```bash
cd braverge
```

Build the project

```bash
# Build instructions will be provided
```

Additional installation instructions and dependencies are available in the documentation.

---

# Documentation

Documentation includes:

* User Guide
* Developer Guide
* Architecture Documentation
* API Documentation
* Examples
* Tutorials
* Benchmark Reproduction Guide

---

# Reproducing the Experiments

The repository contains all artifacts required to reproduce the experimental evaluation reported in the accompanying publication.

These include:

* Benchmark datasets
* Experimental scripts
* Example models
* Configuration files
* Evaluation results
* Supplementary material

Detailed instructions are provided in the `experiments/` directory.

---

# Citation

If you use Braverge in your research, please cite the accompanying publication.

```bibtex
@article{kasaei2026braverge,
  title={Braverge: A Collaborative Model Version Management Framework for Model-Based Systems Engineering},
  author={Kasaei, Seyed Mohammad Sadegh and others},
  journal={...},
  year={2026}
}
```

---

# Contributing

Contributions are welcome.

If you would like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request.

Bug reports, feature requests, and discussions are greatly appreciated.

---

# Contact

**Seyed Mohammad Sadegh Kasaei**

📧 [smskasaei@gmail.com](mailto:smskasaei@gmail.com)

---

# License

This project is released under the **MIT License**.

See the `LICENSE` file for details.

---

# Acknowledgements

Braverge has been developed as part of ongoing research on collaborative model version management, model evolution, and distributed Model-Based Systems Engineering. We thank all collaborators, reviewers, and contributors whose feedback has helped shape the framework.
