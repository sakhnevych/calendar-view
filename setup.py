import setuptools


setuptools.setup(
    name="calendar-view",
    version="2.4.4",
    author="Oleksandr Sakhnevych, Daniil Limariev",
    author_email="o.sakhnevych@gmail.com, danillim02102003@gmail.com",
    description="Library provides a graphical view of the calendar.",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    url="https://github.com/sakhnevych/calendar-view",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Pillow',
    ],
    python_requires='>=3.6',
)
