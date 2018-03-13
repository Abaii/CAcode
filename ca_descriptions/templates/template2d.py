# Name: NAME
# Dimensions: 2

# --- Set up executable path, do not edit ---
import sys
import inspect
import numpy as np
this_file_loc = (inspect.stack()[0][1])
main_dir_loc = this_file_loc[:this_file_loc.index('ca_descriptions')]
sys.path.append(main_dir_loc)
sys.path.append(main_dir_loc + 'capyle')
sys.path.append(main_dir_loc + 'capyle/ca')
sys.path.append(main_dir_loc + 'capyle/guicomponents')
# ---

from capyle.ca import Grid2D, Neighbourhood, randomise2d
import capyle.utils as utils


def setup(args):
    """Set up the config object used to interact with the GUI"""
    config_path = args[0]
    config = utils.load(config_path)
    # -- THE CA MUST BE RELOADED IN THE GUI IF ANY OF THE BELOW ARE CHANGED --
    config.title = "NAME"
    config.dimensions = 2
    #burning states 1-4, non burning 5-8
    # 5 - Chapparral, 6 - Forest, 7 - Canyon, 8-Lake
    config.states = (0,1,2,3,4,5,6,7,8)

    # -------------------------------------------------------------------------

    # ---- Override the defaults below (these may be changed at anytime) ----

    config.state_colors = [(0,0,0),
    (0.847,0.302,0.263),(0.847,0.180,0.133),(0.800,0.090,0.047),(0.486,0.031,0.000),
    (0.923,0.957,0.259),(0.047,0.259,0.019),(0.820,0.816,0.812),(0.137,0.392,0.729)]
    # config.grid_dims = (200,200)

    # ----------------------------------------------------------------------

    # the GUI calls this to pass the user defined config
    # into the main system with an extra argument
    # do not change
    if len(args) == 2:
        config.save()
        sys.exit()
    return config


def transition_function(grid, neighbourstates, neighbourcounts, decaygrid):
    """Function to apply the transition rules
    and return the new grid"""
    cells_in_state_0=(grid==0)
    cells_in_state_1=(grid==1)
    cells_in_state_2=(grid==2)
    cells_in_state_3=(grid==3)
    cells_in_state_4=(grid==4)
    burning_cells = (grid <= 4)
    cells_in_state_5 = (grid == 5) # cells that are currently in state 5
    cells_in_state_6 = (grid == 6) # cells that are currently in state 6
    cells_in_state_7 = (grid == 7) # cells that are currently in state 7
    cells_in_state_8 = (grid == 8) # cells that are currently in state 8
    NW, N, NE, W, E, SW, S, SE = neighbourstates

    #Transition function for Chapparral, Chapparral burns easily and stays on fire for a while
    #Chapparral burns with fewer neighbours, burns higher, and decays slower
    burningNeighbours = (neighbourcounts[1]+neighbourcounts[2]+neighbourcounts[3]+neighbourcounts[4])
    burning_chaparral_neighbours = (burningNeighbours>3)
    burning_chaparral_neighbours_above_one = (burningNeighbours>2)
    burning_chaparral_neighbours_below_four = (burningNeighbours<4)

    rand_burning_chaparral_neighbours = (burning_chaparral_neighbours_above_one & burning_chaparral_neighbours_below_four )

    rand_burning_forest_neighbours = burning_forest_neighbours_above_two & burning_forest_neighbours_below_six
    sample = numpy.random.choice([True, False], (np.size(rand_burning_forest_neighbours,0), np.size(rand_burning_forest_neighbours,1)))

    temp_burning_chaparral_neighbours =  burning_chaparral_neighbours & rand_burning_forest_neighbours[sample]
    chaparral_to_burning = cells_in_state_5 & temp_burning_chaparral_neighbours
    grid[chaparral_to_burning]= 4 #change Chapparral to the highest burn count

    #Transition function for Dense forest, Dense forest doesnt ignite very easily but burns for a long time
    burning_forest_neighbours = (burningNeighbours>5)
    forest_to_burning = cells_in_state_6 & burning_forest_neighbours
    grid[forest_to_burning]=4 #change forest burning

    #Transition function for canyon, burns very easily, only for a few hours
    burning_canyon_neighbours = (burningNeighbours>0)
    canyon_to_burning = cells_in_state_7 & burning_canyon_neighbours
    grid[canyon_to_burning]=4


    decaygrid[burning_cells]-=1
    #add decaygrid[cells_in_state_x] for all states to change the decay rates for different terrains

    decayed_to_three = (decaygrid == 30)
    grid[decayed_to_three]=3

    decayed_to_two = (decaygrid == 20)
    grid[decayed_to_two]=2
    decayed_to_one = (decaygrid==10)
    grid[decayed_to_one]=1
    decayed_to_zero = (decaygrid == 0)
    grid[decayed_to_zero] = 0




    return grid


def main():
    """ Main function that sets up, runs and saves CA"""
    # Get the config object from set up
    config = setup(sys.argv[1:])

    # Create grid object using parameters from config + transition function
    decaygrid = np.zeros(config.grid_dims)
    decaygrid.fill(40)

    grid = Grid2D(config, (transition_function, decaygrid))

    # Run the CA, save grid state every generation to timeline
    timeline = grid.run()

    # Save updated config to file
    config.save()
    # Save timeline to file
    utils.save(timeline, config.timeline_path)

if __name__ == "__main__":
    main()
