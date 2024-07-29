# _Groot_

### _Groot-Cli : A simple version control system built by learning and executing the knowledge gained by using and learing about GIT._


- This is a documentation regarding the usuage , working and purpose of the groot-version control system which is mainly made using the python programming language.
- You ask why python ? Then,I might say that it's my personal prefrence.But,no the main reason to develop it by using _python_ is mainly because of the library support for the _python_.
- Now , lets talk about the _libraries_ you might need to install before getting started.
  - [setuptools] - mainly used to make a package named groot which will work in your Cli.
  - [argparse] - mainly used to take inputs as arguments from the user in the Cli.
  - [subprocess] - mainly used for showing the flow of the commits and files in the Cli.
  - [textwrap] - mainly used to show the commit mesaages in the Cli.
  - [firebase-admin] - used to connect the Cli application with the firebase project and storage bucket.
  - [collections] - mainly used for showing difference between two commits.


### _Important Steps_ :-
- And , pushing your code to your firebase cloud storage you have make some changes in the `groot/remote.py` file.
- make the following changes in the line 13 and 15.

```remote.py
# line 13
cred = credentials.Certificate('path/to/your/private-key.json file')
```
- Here, you have to go to your firebase console -> Project-Settings -> Service Account.
- Then , generate a new private key and replace the `path/to/your/private-key.json file` with the path to your private-key.json files path
- And , then after replacing the path, do the following changes in line 15..

```remote.py
# line 15
'storageBucket': 'your storage bucket name...!'  # Ensure this is just the bucket name without 'gs://'
```
- Here , you need to paste your stoge buckets name from your firebase console
- you can find in the storage section of your firebase project.



### _Getting Started_ :-
- Firstly install all above given libraries and then follow the below given steps to get started...
- open your command prompt and _cd_ to the groot directory.

```sh
cd path/to/your/groot-directory
```
- Then wirte the below given command...

```sh
python setup.py develop --user
```
- Thats all you need to get started with groot.
