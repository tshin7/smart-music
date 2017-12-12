import string
from atexit import register
from copy import deepcopy
from operator import itemgetter

import random
import numpy as np
from psonic import *
from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from pymongo.errors import WriteError
from Naked.toolshed.shell import muterun_rb
from itertools import chain
from instrument_reference import *

# TODO: Optional: Change the code from random.choice to random.choices with probabilities - for granular selection.
# TODO: Continual: improve design of the optimization problem in run_GA_on(), and improve performance as it
#  increases in size.
# TODO: Optional: Change the code to store instrument instructions of all lengths to db and get instructions of a
#  specific length.
# TODO: Optional: Change the code to work with genres in the database and in GA.
# TODO: Optional: Change code so that user midi files are training data, train GA and store populations into midi
# file_name_collection, then make new instrument instructions by...


def main():
    """Prereq: sonic pi must be running to play sounds."""

    # Set for additional console messages
    debug = True

    # Instantiate GA
    ga = GA(debug=debug)

    # Register stop function (stop music) to run upon program termination.
    register(stop)

    user_input = ''

    while user_input != 'exit':
        user_input = input("Enter command for GA: ")

        if user_input == 'play':
            # get song instructions in text form from GA
            # command python sonic run(song_instructions)
            if len(ga.song_instruments) > 0:
                pi_code = ga.get_song_sonicpi_code()
                run(pi_code)
                print('Now playing')
                if debug:
                    print("{} instrument(s) playing.".format(len(ga.song_instruments)))
            else:
                print("Error: Something needs to be on the music stack to get sonic pi code, run add_instrument.")

        elif user_input == 'stop':
            # command python sonic stop()
            stop()
            print('Stopped')

        # elif user_input == 'upload_song': possible addition - if song is really good
        # store song in the db (for use by user, or public top songs chart).

        elif user_input == 'add_instrument':
            ga.push_instrument()
            stop()
            pi_code = ga.get_song_sonicpi_code()
            print('Added {}. {} instrument(s) playing.'.format(ga.song_instruments[-1][2], len(ga.song_instruments)))
            # if in dev mode
            if debug:
                print("Song code (sonic pi):\n{}".format(pi_code))
            run(pi_code)

        elif user_input == 'reset':
            print('Reset')
            # reset ga variable
            ga = GA(debug=debug)
            # command python sonic stop()
            stop()

        elif user_input == 'rate':
            print('Rating...')
            if len(ga.song_instruments) > 0:
                rating = input("Please enter a rating for newest instrument: ")
                if rating.isdigit() and 1 <= int(rating) <= 10:
                    ga.rate_instrument(int(rating))
                    code = ga.get_song_sonicpi_code()
                    if debug:
                        print("Song code (sonic pi):\n{}".format(code))
                    run(code)
                else:
                    print('Error: Rating entered is not a number between 1 to 10.')
            else:
                print('Error: There are no instruments to rate. Run add_instrument.')

        elif user_input == 'apply_ga':
            print('Applying GA')
            # Stop music
            stop()
            # Run ga.
            try:
                ga.run_ga()
                pi_code = ga.get_song_sonicpi_code()
                run(pi_code)
                if debug:
                    print("Song code (sonic pi):\n{}".format(pi_code))
            except IndexError:
                None

        elif user_input == 'toggle_debug':
            debug = not debug
            ga.debug = debug
            print('Debuging is {}'.format("Enabled" if debug else "Disabled"))

        elif user_input == 'set_reference':
            """Sets the GA's instrument_reference and instrument_rating, from a user defined midi file
               and rating. The midi file is processed to conform to the data structure using in the GA."""

            print("Setting reference from MIDI file.")
            args = input("Please enter path to midi_file followed by a Temp folder name to store results:")
            try:
                rating = int(input("Please enter a rating, from 1-10, of this song: "))
                try:
                    # Run midi2spi program to convert midi to txt tracks with notes and store it under
                    # SECOND_ARG/track_XX.txt
                    _ = muterun_rb('midi2spi.rb', args)
                    args = args.split()

                    # load ticks since last note, note duration, and note pitch data from first track
                    # into np.array
                    data = np.genfromtxt("./{}/Track_02.txt".format(args[1]),
                                         delimiter=',',
                                         usecols=(2, 4, 5),
                                         skip_header=11,
                                         dtype=float)
                    if debug:
                        print("Data shape on load: {}".format(data.shape))

                    # try to get an estimated bpm from header that was generated file.
                    bpm = 120
                    try:
                        with open('./{}/header.txt'.format(args[1])) as f:
                            for line in f:
                                line = line.split()
                                if line[0] == 'BPM:':
                                    bpm = int(line[1]) * 6
                                    break
                    except IOError as e:
                        print("I/O error({0}): {1}".format(e.errno, e.strerror))

                    if debug:
                        print("BPM: {}".format(bpm))

                    # Set the sleep vals
                    data[:, 0] = np.round(data[:, 0] / bpm, decimals=3)
                    data[-1, 0] = 1
                    # Set the duration vals
                    data[:, 1] = np.round(data[:, 1] / bpm, decimals=3)

                    # Now put data into our format
                    head = ['live_loop :ref do\n', 'use_synth :', 'piano', '\n', 'with_fx :', 'none',
                            ' do\n']
                    data = [['sleep ', vals[0], '\n',
                             'play ', vals[2], ', amp: ', 1, ', pan: ', 0, ', release: ', 0.5, ', attack: ', 0.03,
                             ', sustain: ', vals[1], ', decay: ', 0.5, '\n',
                             ] for vals in data]
                    data = list(chain.from_iterable(data))
                    end = ['end\nend\n']
                    result = head + data + end

                    if debug:
                        # concat function
                        if len(result) > 0:
                            text = ''
                            text = text + ''.join(str(i) for i in result)
                            print("Final output (Sonic PI):\n{}".format(text))

                    # set the reference instrument in GA
                    ga.instrument_reference = result
                    ga.instrument_rating = rating
                    ga.instrument_reference_name = args[1]
                except FileNotFoundError as fnf:
                    print("Error: Midi txt file not found. {}".format(fnf.strerror))
            except ValueError:
                print("Error: Please enter an integer.")

        elif user_input != 'exit':
            print("""Usage is: GA [options]
            play - Play current GA instruments
            stop - Stop playing GA instruments
            add_instrument - Generate a new instrument and add to instrument stack
            reset - Reset the GA, GA instruments, and GA reference instrument.
            rate - Rate the top most instrument
            set_reference - Set reference midi file and rating to train GA
            apply_GA - Apply Genetic Algorithm to instrument at the top of the instrument stack
            toggle_debug - Toggle additional console output messages
            exit - Exit program\n""")

    print('Program exit.')


class GA:

    def __init__(self, population_size=50,  # Modulates search space size.
                 instrument_size=10,  # Amount of sleep and play note pairs included in instrument track.
                 generations=10,  # Max number of generations to compute before a solution is found.
                 crossover_rate=0.7,  # Crossover probability [0-1)
                 mutation_rate=0.1,  # Mutation probability [0-1)
                 tol=0.1,  # Threshold difference between ref and GA'd instrument scores that count as a solution.
                 use_db=True,  # Specify whether db connection is enabled.
                 debug=False  # Specify for additional console printouts
                 ):

        # Population size: Too large: long epoch time, restricting acceptable generation times.
        #                  Too small: not good coverage of search space.
        # Mutation rate:   Too high: risk of individuals jumping over a solution they were close to.
        #                  Too small: individuals getting stuck in local minimums.

        """Instantiate GA object and member variables to specified values"""
        self.instrument_population = []  # Population array: [ { 'rating': 5, 'instructions': [1,...] }, .... ]
        self.new_instrument_population = []  # New Population array: [ { 'rating': 5, 'instructions': [1,...] }, .... ]
        self.song_instruments = []  # array of array of instrument instructions
        self.song_instruments_ratings = []  # array of ratings from user that correspond to song_instruments.
        self.use_db = use_db
        self.population_size = population_size
        self.instrument_size = instrument_size
        self.generations = generations  # Max generations to iterate over population before tol has been found
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.curr_down_vote_count = 0  # Used to keep count how many downvotes for a instrument a person has made.
        self.tol = tol
        self.debug = debug
        self.instrument_reference = instrument_reference
        self.instrument_rating = instrument_rating
        self.instrument_reference_name = instrument_reference_name
        self.scores_ = []  # Array that stores score values at every generation when run_GA_on() is called.

        """PARAMETERS"""
        self.synths = ['prophet', 'saw', 'dpulse', 'cnoise', 'subpulse',
                       'piano', 'chiplead', 'dull_bell', 'pretty_bell',
                       'hoover', 'pluck', 'tech_saws']
        self.synths_probs = np.array([0.01, 0.04, 0.01, 0.01, 0.02, 0.53, 0.03, 0.05, 0.05, 0.05, 0.1, 0.1])
        self.sleep_vals = [np.arange(0, 2, 0.03), np.arange(0, 2, 0.02)]
        self.play_vals = range(20, 95)
        self.amp_vals = [1]
        self.pan_vals = [0]
        self.release_vals = [0.2, 0.3, 0.4, 0.5]
        self.attack_vals = [0, 0.02, 0.04, 0.06]
        self.sustain_vals = np.arange(0, 0.5, 0.1)
        self.decay_vals = [0.05]
        self.fx_vals = ["none"]

        # sample_vals = [...] optional

        if use_db:
            # connect to MongoDB, change the << MONGODB URL >> to reflect your own connection string
            # client = MongoClient(port=27017)
            client = MongoClient("mongodb://admin1:12345@ds125016.mlab.com:25016/music_db")
            self.db = client.music_db
            # The collections are indexed by '_id' key that is automatically inserted on upload.
            # '_id' is equal to the hash of srt(instrument_instructions)
            # Duplicate instruments are prevented from upload for this reason.

    """Instrument Data Structure: Header: indices 0 - 6, where indices 2 and 5 are synth and fx values respectively.
                                  DATA: indices 7 - (instrument_size*18 - 1), where:
                                    play is followed by 7 floats,
                                    sleep   is followed by 1 float which can take on the values:
                                    [0.0, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0, 1.25],
                                    The sleep and play values alternate between each other.
        I believe this data structure is better than an object because we can access it easier for crossover and
        mutation functions, and we can assume its structure. But this is open to ideas."""

    """Class Methods"""

    def push_instrument(self):
        """Generates and pushes an instrument into the instrument stack, uses GA and DB if db is enabled."""
        if self.debug:
            print("Pushing new instrument")
        # Append to the stack a GA'd instrument
        inst_dict = self.run_ga_on()
        if self.debug:
            print("GA ran and picked best instrument with a rating of {}".format(inst_dict['rating']))
        self.song_instruments.append(inst_dict['instructions'])

    def pop_instrument(self):
        """Pop top instrument from the instrument stack"""

        if len(self.song_instruments) > 0:
            self.song_instruments.pop(-1)
        else:
            print("No instruments to pop from the stack")

    def run_ga(self):
        """Run genetic algorithm on the top item in song_instruments
        Precondition: There has to be an instrument in the song stack and it has to have been rated.
        Postcondition: The instrument at top of the stack will be applied GA"""
        try:
            inst_dict = self.run_ga_on(self.song_instruments[-1], self.song_instruments_ratings[-1])
            if self.debug:
                print("GA ran and picked best instrument with a rating of {}".format(inst_dict['rating']))
            self.song_instruments[-1] = inst_dict['instructions']
        except IndexError:
            print("Error: Something needs to be on the music stack and have been rated to apply GA. " +
                  "Run push_instrument.")
            raise

    def get_song_sonicpi_code(self, start=0):
        """Returns formatted sonic pi code from song_instruments instructions. Optionally, start from
        a specified index from song_instruments where startIndex < len(song_instruments) """

        if len(self.song_instruments) > 0:
            text = ''
            for instrument in self.song_instruments[start:]:
                text = text + ''.join(str(i) for i in instrument)
            return text
        else:
            print("Error: Something needs to be on the music stack to get sonic pi code, run push_instrument.")

    def rate_instrument(self, rating):
        """Rates the instrument at the top of the instrument stack, on a scale of 1 to 10, saves to db if enabled,
        then generates a GA instrument from db or a random one and pushes to the song stack.
        Precondition: self has instrument in stack and rating is 1 <= rating <= 10. Connection to db if enabled.
        Post-condition: instrument in top of stack will have a rating (fitness)"""
        # assert that ga has instrument and 1 <= rating <= 10
        if len(self.song_instruments) > 0 and (1 <= rating <= 10):
            # append rating to song_instruments_ratings
            self.song_instruments_ratings.append(rating)
            # Record user's input to db
            if self.use_db:
                self.upload_instrument(self.song_instruments[-1], rating=rating)
            # perform an update
            if rating >= 5:
                # save topmost instrument to db.
                self.curr_down_vote_count = 0
                # generate (random or from Ga from db) a new instrument and push it onto the song stack.
                self.push_instrument()
            else:
                # increment number of downvotes
                self.curr_down_vote_count += 1
                # if down votes is too much, replace instrument, else mutate it.
                if self.curr_down_vote_count > 3:
                    # delete top instrument and put another one in place
                    self.song_instruments.pop()
                    if self.debug:
                        print("Popped top instrument")
                    self.push_instrument()
                else:
                    self.mutate(self.song_instruments[-1], probability=0.5)
                    if self.debug:
                        print('Mutated instrument.')
        else:
            print('Error in rating: either this GA does not have an instrument or rating is not from 1 to 10.')

    """HELPER FUNCTIONS"""

    def generate_instrument_population(self, instrument, size):
        """Return an array of dicts of instruments, containing rating & instructions, of len=size from db or randomly
        generated. The list will be sorted in descending order of ratings."""
        # Returning result
        result = []
        # Initialize a sample reference rating and instrument to score random instruments against.
        ref_inst = self.instrument_reference[:7+self.instrument_size*18] + ['end\nend\n']
        ref_inst[2] = instrument
        ref_rating = self.instrument_rating

        if self.use_db:
            # get up-to size amount of instrument from db and put into result. Items are dictionaries,
            # sorted by descending ratings.
            result = self.load_instruments(instrument, size)
            if result is None:
                result = []
            # if len(result) != 0:
            #     # Optional
            #     # pick the first most element as reference for use during scoring as it might be better for scoring
            #     # than the hardcoded reference that was assigned above.
            #     if result[0]['rating'] >= ref_rating:
            #         ref_rating = result[0]['rating']
            #         ref_inst = result[0]['instructions']

        # generate new instruments if necessary and add to result.
        for i in range(len(result), size):
            rand_inst = self.generate_instrument(instrument, self.instrument_size)
            result.append({'rating': self.score(rand_inst, ref_inst, ref_rating), 'instructions': rand_inst})
        result = sorted(result, key=itemgetter('rating'), reverse=True)

        return result

    def generate_instrument(self, instrument, size):
        """Returns an array of instrument instructions of data len=size and type=instrument."""

        result = []
        # randomly set sleep intervals to multiples of 0.25 or 0.33
        sleep_val = random.choice(self.sleep_vals)

        # Append Live loop, use_synth, with_fx HEADER
        result.append('live_loop :{} do\n'.format(''.join(random.choices(string.ascii_uppercase, k=5))))
        result.append('use_synth :')
        result.append(instrument)
        result.append('\n')
        result.append('with_fx :')
        result.append(random.choice(self.fx_vals))
        result.append(' do\n')

        # Append play and sleep DATA
        for i in range(0, size):
            result.append('sleep ')                         # index 7, 25,... (7 + (18 * (size-1)) where size > 0)
            result.append(random.choice(sleep_val))         # index 8, 26,... (8 + (18 * (size-1)) where size > 0)
            result.append('\n')                             # index 9, 27,... (9 + (18 * (size-1)) where size > 0)
            result.append('play ')                          # index 10, (10 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.play_vals))    # index 11, (11 + (18 * (size-1)) where size > 0)
            result.append(', amp: ')                        # index 12, (12 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.amp_vals))     # index 13, (13 + (18 * (size-1)) where size > 0)
            result.append(', pan: ')                        # index 14, (14 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.pan_vals))     # index 15, (15 + (18 * (size-1)) where size > 0)
            result.append(', release: ')                    # index 16, (16 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.release_vals)) # index 17, (17 + (18 * (size-1)) where size > 0)
            result.append(', attack: ')                     # index 18, (18 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.attack_vals))  # index 19, (19 + (18 * (size-1)) where size > 0)
            result.append(', sustain: ')                    # index 20, (20 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.sustain_vals)) # index 21, (21 + (18 * (size-1)) where size > 0)
            result.append(', decay: ')                      # index 22, (22 + (18 * (size-1)) where size > 0)
            result.append(random.choice(self.decay_vals))   # index 23, (23 + (18 * (size-1)) where size > 0)
            result.append('\n')                             # index 24, (24 + (18 * (size-1)) where size > 0)
        result.append('end\nend\n')                         # index 25, 43,... (25 + (18 * (size-1)) where size > 0)
        return result

    def run_ga_on(self, ref_inst=None, ref_rating=None):
        """Runs Genetic Algorithm on the reference instrument (ref_inst) or on a sample of picked
         from instrument population and returns a new, GA'd, version of it. Best picks from the population
          will be uploaded to db. Instrument population is either randomly generated or loaded from db.
        Precondition: instrument_instructions and prev_population must be of the same type of instrument
         and of same lengths.
        Post condition: A best pick GA'd instrument will be returned. self.instrument_population will be updated
         with best instruments after GA and will uploaded to db. self.new_instrument_population will be empty."""

        # Print init
        print("Running GA")

        # Reset scores_ to store scores for this run.
        self.scores_ = []

        # Handle the case when generating a new GA instrument or if we are applying GA to existing instrument
        if ref_inst is None:
            # pick a synth (synth list is not exhaustive and changeable)
            instrument = np.random.choice(self.synths, p=self.synths_probs)
            # Load population from database (if enabled) and automatically generate new chromosomes if necessary.
            self.instrument_population = self.generate_instrument_population(instrument,
                                                                             self.population_size)
            ref_rating = self.instrument_rating
            ref_inst = self.instrument_reference
            if self.debug:
                print("Reference name: {}, Reference Rating: {}".format(self.instrument_reference_name, ref_rating))
        else:
            # Load population from database (if enabled) and automatically generate new chromosomes if necessary.
            # In this case we already have a ref_inst and ref_rating so it is not necessary to set one.
            self.instrument_population = self.generate_instrument_population(ref_inst[2],
                                                                             self.population_size)
            if self.debug:
                print("Reference name: {}, Reference Rating: {}".format(ref_inst[2], ref_rating))

        i = 0
        found_solution = False

        while i < self.generations and not found_solution:
            # increment gen count
            i += 1

            # assert new population array is empty
            self.new_instrument_population.clear()

            for _ in range(len(self.instrument_population)):
                # Select two instruments
                inst_1 = self.select_member(self.instrument_population)
                inst_2 = self.select_member(self.instrument_population)
                inst_1_copy = deepcopy(inst_1)
                inst_2_copy = deepcopy(inst_2)

                # Crossover and mutate
                self.crossover(inst_1['instructions'], inst_2['instructions'], self.crossover_rate)
                self.mutate(inst_1['instructions'], self.mutation_rate)
                self.mutate(inst_2['instructions'], self.mutation_rate)

                # Check if a change was made to inst_1 and inst_2, if so continue, else skip loop. We do not have
                # to calculate scores, check for a solution, and add to the new_instrument_population array, inst_1 or
                # inst_2 if they are already known solutions in the instrument population. This helps minimize duplicate
                # instruments appearing in instrument population, however note that they still do appear in an edge
                # case when instruments are crossover or mutated and added to the population, and then are crossover
                # and mutated in a way that sets them back to their original form, and then added back to the population
                if inst_1 == inst_1_copy or inst_2 == inst_2_copy:
                    continue

                # Re-score the instruments. Here we optimize (try to find a solution) to likeness of the ref_inst. In
                # the case we have an item in the stack we want to apply GA, ref_inst=item_in_the_stack. In the case
                # where we just want to randomly generate an instrument from the database or randomly generated
                # population, ref_inst = highest rated instrument from population. Note that randomly generated
                # instruments from self.generate_instrument_population() are pre-scored against a hard coded reference
                # for offline purposes and initial database creation. The reference and inst_1/2 must be same length.
                #  We can later modify this behavior.
                inst_1['rating'] = self.score(inst_1['instructions'], ref_inst, ref_rating)
                inst_2['rating'] = self.score(inst_2['instructions'], ref_inst, ref_rating)

                # if offspring rating is within self.tol of ref_rating we have found a solution.
                if abs(inst_1['rating']-ref_rating) <= self.tol:
                    if self.debug:
                        print("Found a solution of rating={}, within tol={} of reference instrument.".format(
                            inst_1['rating'], self.tol))
                    self.new_instrument_population.append(inst_1)
                    found_solution = True
                    break
                if abs(inst_2['rating']-ref_rating) <= self.tol:
                    if self.debug:
                        print("Found a solution of rating={}, within tol={} of reference instrument.".format(
                            inst_2['rating'], self.tol))
                    self.new_instrument_population.append(inst_2)
                    found_solution = True
                    break

                # Add to the new pool
                self.new_instrument_population.append(inst_1)
                self.new_instrument_population.append(inst_2)

            # Add the new population to the old population
            self.instrument_population.extend(self.new_instrument_population)

            # Only keep the best of the last 3 generations if instrument_population becomes too large to compute.
            if len(self.instrument_population) >= self.population_size * 4:
                # sort the population by descending rating
                self.instrument_population = sorted(self.instrument_population, key=itemgetter('rating'), reverse=True)
                # Prune the instrument_population to prevent it from becoming too large.
                self.instrument_population = self.instrument_population[:self.population_size]

            # Store the training scores for every generation
            score = max(item['rating'] for item in self.instrument_population)
            self.scores_.append(score)

            # Print the current generation training score.
            if self.debug:
                print("Generation: {} Score: {}".format(i, score))

        # At this point, either no solution was found and max number of generations was reached, so choose best pick, or
        # a good enough solution was found so choose it.
        # sort the population by descending rating
        self.instrument_population = sorted(self.instrument_population, key=itemgetter('rating'), reverse=True)

        # Prune the instrument_population to prevent it from becoming too large and upload the best to db.
        self.instrument_population = self.instrument_population[:self.population_size]
        if self.use_db:
            self.upload_instruments(self.instrument_population)

        # New population not needed, release memory.
        self.new_instrument_population.clear()

        return self.instrument_population[0]

    def select_member(self, population):
        """Selects a {rating, instrument} dict from population based on roulette wheel selection
        and returns a copy of it.
        Precondition: population is an array of rating, instrument dicts
        Postcondition: a {rating, instrument} dict from the population is returned."""
        maximum = sum([c['rating'] for c in population])
        pick = random.uniform(0, maximum)
        current = 0
        for chromosome in np.random.choice(population, size=len(population), replace=False):
            current += chromosome['rating']
            if current > pick:
                return deepcopy(chromosome)

    def score(self, instrument, reference, ref_rating):
        """This function scores an instrument based on a known reference instrument and rating. It returns a score
        corresponding to how well the instrument is related to the reference. This is very theoretical. Alternate
        idea for scoring is to have a point scoring system based on known likes and dislikes in music theory.
        Precondition: both instruments must be of the same type and size.
        Post-condition: An integer representing the score of how well the instrument is related to the reference
        is returned."""
        # list of base indices of where the sleep and play data lie
        base_indices = np.array([8, 11, 13, 15, 17, 19, 21, 23])
        # Create an array of indices from base indices for specific instrument
        indices = np.mgrid[0:self.instrument_size*18:18, 0:8][0]
        indices = np.ravel(indices + base_indices)
        # get the sleep and play data from instrument and reference
        inst_data = np.array(itemgetter(*indices)(instrument))
        ref_data = np.array(itemgetter(*indices)(reference))
        # calculate instrument and reference difference
        differences = np.abs(inst_data - ref_data)
        sum_of_diffs = np.sum(differences)
        # return an estimated rating based on differences
        if sum_of_diffs == 0:
            return ref_rating
        else:
            # 90 is max ins vs ref difference for instrument of size 1. This line might result in floats.
            return ref_rating - (ref_rating * sum_of_diffs/(83.96*self.instrument_size))

    def crossover(self, instrument1, instrument2, probability):
        """Crossover: Select a point in instrument1,
        swap contents of each array from that point on.
        Side Affects instrument1, instrument2"""
        make_change = np.random.random() < probability

        if make_change:
            # select random index in instrument data (not header)
            crossover_index = instrument1.index(random.choice(instrument1[7:]))
            swap = instrument1[crossover_index:]
            # swap
            instrument1[crossover_index:] = instrument2[crossover_index:]
            instrument2[crossover_index:] = swap

    def mutate(self, instrument, probability):
        """Rolls a dice for random mutation of instructions in array. Note: The items that can be mutated will
        not include the header. This function has side effects."""
        # list of base indices of where the sleep data lie
        indices = np.arange(8, self.instrument_size * 18, 18)

        # for each data val in instrument, run the appropriate mutation with the probability
        for index in indices:
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index] = random.choice(random.choice(self.sleep_vals))
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+3] = random.choice(self.play_vals)
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+5] = random.choice(self.amp_vals)
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+7] = random.choice(self.pan_vals)
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+9] = random.choice(self.release_vals)
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+11] = random.choice(self.attack_vals)
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+13] = random.choice(self.sustain_vals)
            # roll dice
            make_change = np.random.random() <= probability
            if make_change:
                instrument[index+15] = random.choice(self.decay_vals)

    """Mongo DB Services"""

    def upload_instrument(self, instrument, rating):
        """Upload an instrument with a rating into music_db's instrument_collection collection.
        Instrument: sonic pi code array (chromosome).
        Rating: integer representing the instrument's rating.
        Precondition: Connection to db. All instrument lengths must match in DB and in instrument and length
         must be non zero. Rating must be between 1 and 10.
        """
        try:
            data = {
                "_id": hash(str(instrument)),
                "rating": rating,
                "instrument": instrument[2],
                "instructions": instrument
                # TODO: "genre": genre
            }
            self.db.instrument_collection.update({'_id': data['_id']}, data, True)
            if self.debug:
                print("Uploaded instrument")
        except WriteError as wr:
            print("Error on upload_instrument: {}".format(wr.details))

    def upload_instruments(self, instruments):
        """Upload population (rating,instructions) dicts into music_db's instrument_collection collection.
        instruments: an array of dictionaries with rating and instructions keys and values.
        Precondition: Connection to db. All instrument lengths must match in DB and instrument length
         must be non zero. Rating must be between 1 and 10.
        Postcondition: If successful, the instruments will be upload to db, if not, then an error will be printed.
        """
        try:
            # add "instrument" key and value to each dictionary in "instruments" array.
            data = [dict(inst, instrument=inst['instructions'][2], _id=hash(str(inst['instructions'])))
                    for inst in instruments]
            # TODO: "genre": genre
            self.db.instrument_collection.insert_many(data, ordered=False)
            if self.debug:
                print("Uploaded instruments")
        except BulkWriteError as bwe:
            print("Error on upload_instruments: {}".format(bwe.details))
            # werrors = bwe.details['writeErrors']
            # print(werrors)

    def upload_song(self, song, rating):
        """Uploads a song array, along with it's rating to music_db's song_collection collection.
        song: array of sonic pi instruments.
        Rating: integer representing the song's rating.
        Precondition: DB connection. Length of song must be non zero. Rating must be between 1 and 10.
        """
        try:
            data = {
                "_id": hash(str(song)),
                "rating": rating,
                "instruments": song
                # TODO: "genre": genre
            }
            self.db.song_collection.update({'_id': data['_id']}, data, True)
            if self.debug:
                print("Uploaded song")
        except WriteError as wr:
            print("Error on upload_song: {}".format(wr.details))

    def load_instruments(self, instrument_type, size):
        """Returns an array of instruments, of kind instrument_type, of size self.population_size. The data is get
        from music_db's instrument_collection collection and is sorted by rating in descending order.
        instrument_type: a valid instrument type (piano, saw, prophet, etc.) from db.
        Precondition: instrument_type must be a valid instrument type in the database. DB connection.
        Postcondition: A list which contains instrument dictionaries with rating and instructions is returned.
        """
        try:
            data_cursor = self.db.instrument_collection.find({"instrument": instrument_type},
                                                             projection={"_id": False,
                                                                         "instrument": False},
                                                             limit=size,
                                                             sort=[('rating', -1)])
            result = list(data_cursor)
            if self.debug:
                print("Loaded {} {}s from DB.".format(len(result), instrument_type))
            return result
        except Exception:
            print("Failed to load instruments. {}".format(Exception.__str__))

    def load_song(self, song_id):
        """Gets a song from music_db's song_collection collection identified by song_id.
        song_id: a valid key of a song object in song_collection collection.
        Precondition: song_id must be a valid key in the song_collection. DB connection.
        Postcondition: A list which contains the song dict is returned. Song dict contains rating and instruments.
        """
        try:
            data_cursor = self.db.song_collection.find_one({"_id": song_id},
                                                           projection={"_id": False})
            result = list(data_cursor)
            if self.debug:
                if len(result) > 0:
                    print("Song loaded")
                else:
                    print("No song found.")
            return result
        except Exception:
            print("Failed to load song. {}".format(Exception.__str__))

            # def update_song_rating(self, song_id):
            # update db


main()
