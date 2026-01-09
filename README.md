# Version Control System (VCS) with Web API

This project is a web-based version control system with support for a RESTful Web API, developed as a educational project. It demonstrates the core principles of version control systems, server-side file system organization, change history management, and API design for interaction with external clients.

The project implements the basic functionality of systems similar to Git in a simplified, application-level form, with a focus on web development, client–server architecture, and API design.

## Features

The system supports user registration and authentication. Each user can create and manage their own repositories, work with the file structure, and manipulate text files and directories. Available operations include creating, editing, deleting, and uploading files.

A key component of the system is the change tracking mechanism based on milestones. A user can record the current state of a repository by creating a milestone, which stores both the list of performed actions and a complete snapshot of the repository at that moment. The change history allows users to review all previous states and restore the repository to any selected milestone.

The system also supports repository cloning, granting access rights to other users, deleting repositories, and downloading repositories as archives.

## Project Extension: Web API

The system was extended by implementing a Web API that provides programmatic access to the core functionality of the version control system. The API follows REST architectural principles and allows interaction with the system without using the web interface.

Through the API, clients can perform user authentication, create and manage repositories, work with files and directories, retrieve change history, create milestones, and restore repositories to previous states. Data exchange is performed in JSON format, ensuring easy integration with external services or client applications.

The Web API enables the system to be used as a backend for third-party clients, including web, desktop, or mobile applications, and demonstrates an approach to scaling web applications by separating the user interface from server-side logic.

## System Architecture

The repository file system is organized on the server as separate directories for each repository. Each repository contains a directory for the current content and a history directory that stores archived snapshots corresponding to each milestone.

All user actions related to file and directory changes are recorded as a list of changes. After a milestone is created, this data is stored in the database and used to restore previous versions of the repository.

## Technologies Used

The project is implemented using the Python programming language and the Django web framework. The Web API is built with Django REST Framework. Data storage is handled by the MySQL relational database management system.

Django is responsible for business logic, database interaction, and server-side application behavior, while the Web API provides standardized programmatic access to the system’s functionality.

## Project Purpose

This project has an educational and practical focus and is intended for in-depth study of web development, version control system principles, REST API design, and client–server architecture. It demonstrates the evolution from a traditional web application to a full-featured server-side platform with an API ready for integration with external clients.
