from setuptools import setup

setup(
    name='django-jellyroll-expansion-pack',
    version='0.1.0.a1',
    author=u'Benjamin Turner',
    author_email='benturn@gmail.com',
    packages=[
        'jellyroll_expansion_pack',
        'jellyroll_expansion_pack.providers',
    ],
    url='https://github.com/blturner/jellyroll-expansion-pack',
    # license='BSD',
    description='Extra providers for django-jellyroll.',
    zip_safe=False,
    install_requires=[
        'Django>=1.4,<1.7',
        'jellyroll>=1.0',
    ],
    test_suite='stardate.tests'
)
