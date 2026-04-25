from abc import ABC, abstractmethod

class PhysicsConstraintError(Exception):
    pass

class RollingStock(ABC):
    # abstract base class for all rolling stock (locomotives and freight cars)
    def __init__(self, id_str: str, weight: float):
        self.id_str = id_str
        self.weight = weight

    @abstractmethod
    def total_weight(self) -> float:
        pass

class Locomotive(RollingStock):
    # locomotives have pull capacity and fuel rate in addition to weight
    def __init__(self, id_str: str, weight: float, pull_capacity: float, fuel_rate: float):
        super().__init__(id_str, weight)
        self.pull_capacity = pull_capacity
        self.fuel_rate = fuel_rate

    def total_weight(self) -> float:
        return self.weight

class FreightCar(RollingStock):
    # freight cars have cargo weight and destination in addition to empty weight
    def __init__(self, id_str: str, empty_weight: float, cargo_weight: float, destination: str):
        super().__init__(id_str, empty_weight)
        self.cargo_weight = cargo_weight
        self.destination = destination

    def total_weight(self) -> float:
        return self.weight + self.cargo_weight 

class Train:
    def __init__(self):
        self._stock: list[RollingStock] = []

    def couple(self, stock: RollingStock):
        # add a locomotive or freight car to the train
        self._stock.append(stock)

    def uncouple(self, stock_id: str) -> RollingStock:
        # remove a rolling stock by id and return it
        for i, s in enumerate(self._stock):
            if s.id_str == stock_id:
                removed = self._stock.pop(i)
                return removed
        raise ValueError(f"No stock with id '{stock_id}' found on train.")

    def get_total_weight(self) -> float:
        return sum(s.total_weight() for s in self._stock)

    def get_total_pull(self) -> float:
        return sum(s.pull_capacity for s in self._stock
                   if isinstance(s, Locomotive))

    def validate_physics(self):
        # check if total weight exceeds total pull capacity, and raise an error if it does
        total_w = self.get_total_weight()
        total_p = self.get_total_pull()
        if total_w > total_p:
            raise PhysicsConstraintError(
                f"Physics violation! Total weight {total_w}t "
                f"exceeds pull capacity {total_p}t."
            )

    def get_average_fuel_rate(self) -> float:
        locos = [s for s in self._stock if isinstance(s, Locomotive)]
        if not locos:
            raise PhysicsConstraintError("No locomotives on train!")
        return sum(l.fuel_rate for l in locos) / len(locos)

    def get_freight_cars(self) -> list:
        return [s for s in self._stock if isinstance(s, FreightCar)]

class RailwayNetwork:
    def __init__(self):
        self._graph: dict[str, dict[str, float]] = {}

    def add_link(self, station_a: str, station_b: str, distance: float):
        # undirected graph: add distance for both directions
        self._graph.setdefault(station_a, {})[station_b] = distance
        self._graph.setdefault(station_b, {})[station_a] = distance

    def get_distance(self, station_a: str, station_b: str) -> float:
        try:
            return self._graph[station_a][station_b]
        except KeyError:
            raise ValueError(f"No direct link between '{station_a}' and '{station_b}'.")

def run_delivery_schedule(train: Train, network: RailwayNetwork, route_list: list[str]) -> float:
    # simulate the train moving through the route, uncoupling freight cars at their destinations,
    total_fuel = 0.0

    for i, station in enumerate(route_list):
        cars_to_drop = [car for car in train.get_freight_cars() if car.destination == station]
        for car in cars_to_drop:
            train.uncouple(car.id_str)

        if i == len(route_list) - 1:
            print("Final destination reached.")
            break

        next_station = route_list[i + 1]

        train.validate_physics()
        print(f"  [OK] Physics check passed. "
              f"Weight={train.get_total_weight()}t, "
              f"Capacity={train.get_total_pull()}t")

        distance       = network.get_distance(station, next_station)
        weight         = train.get_total_weight()
        avg_fuel_rate  = train.get_average_fuel_rate()
        fuel           = weight * distance * avg_fuel_rate
        total_fuel    += fuel

        print(f"  [DEPART] {station} → {next_station} | "
              f"{distance} km | {weight}t × {distance}km "
              f"× {avg_fuel_rate} = {fuel:.1f} L")

    return total_fuel

# put your input here

net = RailwayNetwork()
net.add_link("Delhi",  "Kanpur",     400)
net.add_link("Kanpur", "Prayagraj",  200)

train = Train()
train.couple(Locomotive("L1", weight=100, pull_capacity=500, fuel_rate=0.01))
train.couple(FreightCar("C1", empty_weight=20, cargo_weight=80,  destination="Kanpur"))
train.couple(FreightCar("C2", empty_weight=20, cargo_weight=180, destination="Prayagraj"))

total_fuel = run_delivery_schedule(train, net, ["Delhi", "Kanpur", "Prayagraj"])
print(f"Total Fuel Consumed: {total_fuel}")