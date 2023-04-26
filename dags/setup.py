import os
import setuptools

package_name = 'antaq_dag'

root_packages = [
    'tasks',
    'tools',
]

packages = [package_name] + [
    f'{package_name}.{package}'
    for package in root_packages
]

package_dirs = {package_name: '.'}
package_dirs.update({
    f'{package_name}.{package}': os.path.join(*package.split('.'))
    for package in root_packages
})

package_data = {package_name: [
    "__init__.py",
]}

exclude_package_data = {package_name: [
    "*__pycache__*"
]}

base_path = os.path.dirname(os.path.abspath(__file__))

setuptools.setup(
    name=package_name,
    version="0.0.0",
    author="Eduardo Luiz",
    author_email="eduardo.luizgs@hotmail.com",
    description="Pipeline de dados da Antaq",
    url="",
    packages=packages,
    package_dir=package_dirs,
    package_data=package_data,
    exclude_package_data=exclude_package_data,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux/Ubuntu",
    ]
)
