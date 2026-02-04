fpa.circ contains the design
Note: it is built in Logisim Evolution.

The core algorithm is demostrated in fpa.py
The hardware implementation accurately follows this logic with some simplication and optimization.
It would be helpful to understand the python implementaion first.

convert.py and test.py are helpful for testing purposes.

There are still a lot of inefficiencies. In many places I used built is components that are not explicitly allowed.
In some other places I used simpler implimantation that is expensive, whereas better implementation requires more complex logic (mostly in normalization block, it would be more efficient to use barrel shifter).

After making edits, use the test cases from test.py for validity.