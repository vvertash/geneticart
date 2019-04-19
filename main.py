import numpy
import sys
from copy import deepcopy
from PIL import Image, ImageDraw, ImageChops

# input image
input_image = Image.open('input.jpg').convert('RGBA')

# variables
population_size = 20
fitness = 1000

# number of iterations
iterations = 5000

# circles radius
radius = 10

# iteration index
index = 50

#cache size
cache = 1000

# random variables
random_x_counter = 0
random_x = None
random_y_counter = 0
random_y = None

# fitness function (root mean square difference)
def fitness_func(image):
    rms = ImageChops.difference(image, input_image)
    histogram = rms.histogram()
    squares = (value * ((index % 256) ** 2) for index, value in enumerate(histogram))
    squares_sum = numpy.sum(squares)
    answer = squares_sum / float(512 * 512)
    return answer

# random optimizers functions
def random_func(random_array, random_counter, min_value, max_value, shape):
    if random_array is None:
        random_array = numpy.random.randint(min_value, max_value, shape)
    answer = random_array[random_counter]
    random_counter += 1
    if random_counter == cache:
        random_counter = 0
        random_array = numpy.random.randint(min_value, max_value, shape)
    return answer, random_array, random_counter

def random_x_func():
    global random_x, random_x_counter
    answer, random_x, random_x_counter = random_func(random_x, random_x_counter, 0, 512, cache)
    return answer

def random_y_func():
    global random_y, random_y_counter
    answer, random_y, random_y_counter = random_func(random_y, random_y_counter, 0, 512, cache)
    return answer

# mutation function
def mutation(image):
    canva = ImageDraw.Draw(image)
    color = numpy.random.randint(0, 256, 3)
    color = (color[0], color[1], color[2], 255)
    x = random_x_func()
    y = random_y_func()
    canva.ellipse([(x, y), (x + radius, y + radius)], fill=color, outline=color)
    return image

# blending two images
def blend_images(image1, image2):
    return Image.blend(image1, image2, 0.5)

# creating an image
def create_image():
    return Image.new('RGBA', (512, 512), (0, 0, 0, 255))

# learning function
def learn(fitness):

    # making population list
    population = list()

    # taking output image or creating a new one
    try:
        cash_image = Image.open('output.png').convert('RGBA')
    except FileNotFoundError:
        cash_image = create_image()

    # checking fitness
    if fitness_func(cash_image) < fitness:
        return

    # filling population
    for i in range(population_size):
        population.append(deepcopy(cash_image))

    # miking best and pre_best variables
    best = None
    pre_best = None

    # making fitness
    for i in range(iterations):
        best_fitness = sys.float_info.max

        for individual in population:
            current_fitness = fitness_func(individual)

            if best is None or fitness_func(individual) <= best_fitness:
                pre_best = best
                best = individual
                best_fitness = current_fitness

        # making new population
        new_population = list()
        new_population.append(best)
        new_population.append(pre_best)

        population.remove(best)
        if pre_best in population:
            population.remove(pre_best)

        # blending two images
        blend = blend_images(best, pre_best)

        # filling new population
        for individual in population:
            new_population.append(mutation(deepcopy(blend)))

        # updating population
        population = new_population

        # printing number of iteration
        if i % 100 == 0:
            best.save('output.png')
            print('Iteration: ' + str(i))

            # checking fitness
            if best_fitness < fitness:
                return

    # saving output image
    best.save('output.png')

# running genetic algorithm
learn(fitness)