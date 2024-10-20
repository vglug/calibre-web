# Base class (Parent)
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound."

# Derived class (Child) inheriting from Animal
class Dog(Animal):
    def speak(self):
        return f"{self.name} barks."

# Creating an object of the derived class
dog = Dog("Buddy")
print(dog.speak())  # Output: Buddy barks.
