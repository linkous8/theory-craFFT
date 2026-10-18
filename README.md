# Theory CraFFT

Theory crafting for Final Fantasy Tactics

## Installation
1. Follow the Google sheets Python "Quickstart" (Nothing is quick about this -_-)
    * https://developers.google.com/workspace/sheets/api/quickstart/python
1. Drop the downloaded json file into this folder.
1. Create a sheet in your google account to use as the destination for table generation
1. Note the sheet ID that is in the URL of your browser. eg.
    * https://docs.google.com/spreadsheets/d/**SHEET_ID_IS_HERE**/edit?gid=12341234#gid=123412334
1. Copy the .env_template file and rename the copy .env
1. Update the sheet ID value
1. Install the uv python runtime and virtual environment manager
    * https://docs.astral.sh/uv/
1. Run `uv install`
1. Run `make run` to populate it with the parsed and transformed data from the data folder

There are various additional utilities that were useful in writing this program.
Run `make help` to get a full list of commands and descriptions

## About this project

Final Fantasy Tactics Advance is a game I enjoyed greatly in my younger years 
that I started replaying recently. I came to find out that classes have specific
amounts that stats increase by on level up which makes some classes better to 
level as depending on what you plan to use the character for

After watching [this youtube video](https://www.youtube.com/watch?v=tF5TvKMbRFs) 
I went down a min-maxing rathole trying to figure out which jobs to level as. I 
found a nifty table on gamefaqs with the exact info I was looking for but it was 
still difficult to actually compare the opportunity cost of leveling as certain 
classes against the ubiquotously powerful speed stat. 

I thought a heatmap would help and started a google sheet 
by hand. I was able to apply the gradient rule easily enough... for one range of 
cells. Each range of cells required like 10 clicks to apply a single gradient
which had to be repeated for each stat column of each table. Being a softare
engineer, I thought "screw this, I'll whip up a quick script to automate this".
It was not quick (AI would have been quicker but efforts like this help me keep 
me from losing my edge). As I continued working on it, the scope expanded:
adding min-max normalization, adding qualitative (read: rough attempt at) derived 
stats, header styling, etc.

Eventually it did come together as a roughly constructed framework for these 
sorts of things in the future. I may put together a set of tables for Dragons 
Dogma if I get around to replaying that roughest of diamonds.

There's plenty more to improve on but at this point I am out of steam, this is 
shared for the sake of others who want this information or want to be able to
theory craft like this with less manual excel clicking and data entry
