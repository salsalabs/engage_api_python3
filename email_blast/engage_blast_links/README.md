# engage_blast_links
Retrieve a CSV of all email blast URLs for an Engage client.

# Summary
This application uses the Engage Website Developer API to retrieve a list of email blasts
from an Engage client.  The list of email blasts contains the usual identity information.
It also contains the public-facing URL for the email blast.

The public-facing URL for the blast can be placed into a client's website as a way to let
supporters see past blasts.

## Implementation Note

In order for this app to be usefull to Salsa staffers, it's been developed in  Python version 2.7
Python 2.7 is an old and creaky version that just needs to be hauled off.  However, it's the version that
appears in MacOSX, and all of the folks that would use this app inSalsa are on Macs, so we're stuck with it.

TL;DR

This section is for folks that don't no stinkin' installation docs.  Use at your own risk.

_Do not_ come whining to me if you use these steps and your computer blasts off into the ceiling,
showering you with little bits of ceiling tile, insulation and concrete. Capisce?

Open a terminal window and folow these steps.  You'll need a ```Projects``` directory in your homedir
for this to be effective.


```
sudo easy_install pip
pip install unicodecsv pyyaml 'requests>=2.23.0'
cd ~/Projects
git clone https://github.com/salsalabs/engage_blast_links.git
cd engage_blast_links
```

If you get here without any egregious errors, then proceed at best speed to the section
labeled "Configuration".

# Prerequisites

This is a checklist of the things that you _must have_ before you install this application.
If you do not have any items in this list then STOP.  Get help from one of the technical types
in Salsa Client support.

* Git

The ```git``` app is the tool that's used to access a Github repository.  We need ```git```
because Salsa has stored the app in a git repository.

Finding and installing git is outside the scope of this document.  You might try using
[BrewPub](https://brew.sh/), an excellent tool for installing software on a Mac.  You can also
go directoy to [the git site](https://git-scm.com/) and download from there.

* Python version 2.7.

The best way to find out if you have Python 2.7 is to open a Terminal window (_not_ a Console window)
and type this at the prompt.

``` python --version```

You should see something like this.

```Python 2.7.16```

You have the right version of Python if
* the Python program exists, and
* you get a message that says that the Python version is ```2.x```, where ```x``` is 7 or greater, and
* you do not get a message that says that the version is ```3.x```

If you do not see those three things, then STOP.  Get help installing Python 2.7.

* Password for your Mac

If you are logged into your Mac, then you have the password for it.  If you're not logged in, then
STOP.  Contact IT Corporate Support.

* Web Developer API token for Engage.

_Caution_: If you haven't got a clue about what this means, then
it's [time to read the doc](https://help.salsalabs.com/hc/en-us/articles/360001220274-General-Information)
and [read the other doc](https://help.salsalabs.com/hc/en-us/articles/360001175053-Web-Developer-API-Overview).
That will give you the info that you need to return the Web Developer API token.

If you're still confused after reading the doc the STOP.  Get help from [SalsaSupport](mailto:support@salsalabs.com).

# Installation

The application is installed in two steps.

1. Install the app's dependencies.
2. Install the app itself.

## Dependencies

This application needs one administrative tool and three libraries.

* PIP

PIP is the tool that Python uses to install libraries.  There's a pretty good chance that you don't have
this installed if you are working on a Mac.  Given those odds, let's just go ahead and install PIP.

Open a Terminal window and type this line.

```sudo easy_install pip```

You'll be prompted for a password.  Type in the password that you used to log into your Mac.  If you're not successful,
the you'll get another prompt for your password.  If you fail three attempts then STOP.  You're not using the
correct password.  Contact IT Corporate Support.

If you see an error message indicating that easy_install doesn't exist, then STOP.  Contact IT Corporate Support.

If the installation is working, you'll see a lot of text go by.  Some of it may be yellow.  There might be a progress bar.

To confirm that pip is installed, type this.

```pip```

You'll see the pip help options.

```Usage:
  pip <command> [options]

Commands:
  install                     Install packages.
  download                    Download packages.
  uninstall                   Uninstall packages.
  freeze                      Output installed packages in requirements format.
  list                        List installed packages.
  show                        Show information about installed packages.
  check                       Verify installed packages have compatible dependencies.
  config                      Manage local and global configuration.
  search                      Search PyPI for packages.
  wheel                       Build wheels from your requirements.
  hash                        Compute hashes of package archives.
  completion                  A helper command used for command completion.
  debug                       Show information useful for debugging.
  help                        Show help for commands.

General Options:
  -h, --help                  Show help.
```
If pip is not installed the STOP and get help installing pip.

## Libraries

The libraries that this app needs are installed using pip.  Open a terminal window and type this.

```pip install unicodecsv pyyaml 'requests>=2.23.0'```

Pip will retrieve the libraries.  Usually takes just a bit.  If pip stops and complains, then that's
an error.  STOP.  Get help installing the libraries.

# Install the app

1. Open a console window.
2. Change to the directory where you want the app's directory to live.  We'll use the ```Projects```
folder that appears in nearly everyone's home directory.  Type this.
``` cd ~/Projects```.
3. Retrieve the app directory from Github.
```git clone https://github.com/salsalabs/engage_blast_links.git```

If git complains then STOP.  Get help with git.

#Configuration

The application needs to know which Engage instance to use when retrieving email blast information.
We provide that information in a YAML login file.  A YAML file is a text file with a straightforward format.
Here's an example of the contents of a YAML login file.

```yaml
devToken: your enormously long Engage Web Developer API token here
```

Here's a more detailed definition of what goes into the YAML login file.

| Field name | Contents | Notes | Example |
| ---------- | -------- | ----- | ------- |
|token | Integration API token | Not used for this app | ```token: REWQTERWEQR#$@#$@```|
|host  | Integration API host | (optional) defaults to api.salsalabs.org| ```host: hq-ua.igniter.bof```|
|devToken| Web Developer API token| Required for this app |  ```devToken: REWQTERWEQR#$@#$@```|
|devHost | Web Developer API host | (optional) defaults to dev-api.salsalabs.org| ```devHost: hq-ua.igniter.bof```|


The best way to create this file is to use a text editor.  A good practice is to put a useful name on the file
like "client.yaml" or "peanut_butter.yaml" so that you'll know what's in the file.  We'll use the YAML login
file in the "Execution" step.

#Execution

This is where we _finally_ get things started.

First, let's make sure that the app is running correctly.  Open a terminal window and type this.

```python email_blast_links.py --help```

You should see this.

```
usage: email_blast_links.py [-h] [--login LOGINFILE]

Display email blast URLs for Engage

optional arguments:
  -h, --help         show this help message and exit
  --login LOGINFILE  YAML file with login credentials
```

If you don't see that, then STOP and get help running a Python program.

To run the application, provide a login YAML file.  For this example, we'll use "squirrels.yaml".
it's a file with contents like this.

```yaml
token: devToken: REWQTERWEQR#$@#$@
```

To extract the Enage blast information using "squirrel.yaml", type this.

`python email_balst_links.py --login squirrel.yaml`

You'll see text like this:

```
mail_blast_links.py:34: YAMLLoadWarning: calling yaml.load() without Loader=... is deprecated, as the default Loader is unsafe. Please read https://msg.pyyaml.org/load for full details.
  cred = yaml.load(open(args.loginFile))
 10/400
 20/400
 30/400
 40/400
 50/400
 60/400
 70/400
 80/400
 90/400
100/400
   .
   .
   .
Output may be found in email_blasts_urls.csv
```

Disregard the "YAMLLoadWarning" message.

The status lines contain the number of records read, a slash, and the number of records to read.
The status lines continue until the job is done.
The last ine lets you know where the CSV with the results lives.  Open that file, and you'll see something like this.

```csv
id,name,title,subject,hasUrl,url
f6bee63d-3efb-4615-888a-133f5f229d36,01 IWD preview email - 02.17.20,A preview just for you...,"<span ignite-mergefield-default=""Friend"" ignite-mergefield-id=""5d5a2165-f19e-4371-851b-183a6b92402b"" ignite-mergefield-option=""none"" ignite-text=""First Name"">First Name</span>, a preview just for you...",True,https://fistulafoundation.salsalabs.org/iwd2020_1
78df7c14-798e-4ed8-9529-132dc3e826e8,02  IWD LAUNCH email - 02.18.20,♀️ Support Afghan women helping women,♀️ Support Afghan women helping women,True,https://fistulafoundation.salsalabs.org/iwd2020_2
f9c297b5-3833-419a-8ca8-d7069b54cf35,03 IWD $20k MATCH announcement - 2.20.20,🎉 Gifts MATCHED for Intl. Women's Day!,🎉 Gifts MATCHED for Intl. Women&#39;s Day!,True,https://fistulafoundation.salsalabs.org/iwd2020_3_20kmatch
91662808-0758-4b8e-8919-493e7c575d18,03  IWD  email - Meet the Team 02.20.20,I'm inspired by these women,I&#39;m inspired by these women,True,https://fistulafoundation.salsalabs.org/iwd2020_3
a6c1f4b9-5976-46de-906f-fb6a7194cc70,05 IWD all female doctors - 2.25.2020,👩‍⚕️ Women helping other women,👩&zwj;⚕️ Women helping other women,True,https://fistulafoundation.salsalabs.org/iwd2020_5
9389679d-5731-417c-aabf-4987a38a6787,06 IWD meet Dr. Hema,"""They are forgotten by everyone""",&quot;They are forgotten by everyone&quot;,True,https://fistulafoundation.salsalabs.org/iwd2020_6
1bb76074-c930-4e0d-9298-37239c3d61e9,07 IWD $20k MATCH announcement - 3.02.20,♀️ MATCH for Int'l Women's Day!,♀️ MATCH for Int&#39;l Women&#39;s Day!,True,https://fistulafoundation.salsalabs.org/iwd2020_7
3806fa6f-dd65-409f-9d80-5b7e30494c21,1.23.18 - Monthly Donor email (General) ($500-$1k),I know you care...,"<span ignite-mergefield-default=""Friend"" ignite-mergefield-id=""5d5a2165-f19e-4371-851b-183a6b92402b"" ignite-mergefield-option=""none"" ignite-text=""First Name"">First Name</span>, I know you care...",True,https://fistulafoundation.salsalabs.org/monthly_giving_012318b
3806fa6f-dd65-409f-9d80-5b7e30494c21,1.23.18 - Monthly Donor email (General) ($500-$1k),Your today is her tomorrow,"<span ignite-mergefield-default=""Friend"" ignite-mergefield-id=""5d5a2165-f19e-4371-851b-183a6b92402b"" ignite-mergefield-option=""none"" ignite-text=""First Name"">First Name</span>, your today is her tomorrow",True,https://fistulafoundation.salsalabs.org/monthly_giving_012318d
```

Each line represents an email blast that has a URL.  Each line contains these fields.

| Field Name | Content |
| ---------- | ------- |
| id | Engage ID for the email blast.  Very long. |
| name| The email blast's name |
| title | The email blast's title |
| subject | The subject line that recipients see |
| hasUrl | True |
| url | The email blast's public-facing URL.  Can have a _bunch_ of embedded HTML |

# Cleanup

You may want to delete the CSV file after you've sent it to the client.

You _will defintely_ want to delete the login YAML file. Secure the client's interests, whack that file and empty the trash.

# Questions?  Comments?

If you have any questions or comments, then use the Issues link at the top of this repository.
Do not both Salsa Customer Service with quesitons about this app.  It's their nesting season and
they bite.
