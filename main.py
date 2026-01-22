import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.approximation as nx_app

import argparse
import pathlib
import sys

import waypoint


def get_args():
    parser = argparse.ArgumentParser(
        prog="route-planner",
        description="Finds a route between structures in a minecraft world using the Christofides algorithm",
        epilog="Written by lainon for the University of Sussex Minesoc survival server",
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="path to the structures.csv file exported by cubiomes viewer",
    )

    parser.add_argument(
        "-s",
        "--structure",
        type=lambda s: s.lower(),
        required=True,
        help="the kind of structure we're interested in",
    )
    parser.add_argument(
        "-d",
        "--details",
        type=str,
        required=False,
        help="additional details for the structure",
    )
    parser.add_argument(
        "-o",
        "--origin",
        nargs=2,
        type=int,
        help="the starting (x, z) position of our route, defaults to (0, 0)",
        default=(0, 0),
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="the number of structures to consider",
    )

    parser.add_argument(
        "--show-total-distance",
        action="store_true",
        default=False,
        help="display the total distance of the route",
    )
    parser.add_argument(
        "--use-regex-in-details",
        action="store_true",
        default=False,
        help="use regex matching in structure details",
    )

    waypoint_opts = parser.add_argument_group(
        "Waypoint options", "Xaero waypoint options"
    )
    waypoint_opts.add_argument(
        "-w",
        "--save-waypoints",
        action="store_true",
        help="write the route to xaeros minimap as a set of numbered waypoints",
        default=False,
    )

    waypoint_opts.add_argument(
        "--waypoint-dir",
        help="root directory of xaeros minimap waypoints for the world or server",
        type=str,
    )

    waypoint_opts.add_argument(
        "--waypoint-colour",
        help="the waypoint colour",
        type=int,
        default=5,
        choices=range(16),
    )

    waypoint_opts.add_argument(
        "--route-name",
        help="the name of the route",
        type=str,
    )

    waypoint_opts.add_argument(
        "--waypoint-type",
        type=int,
        choices=range(4),
        default=0,
        help="waypoint type specification",
    )
    waypoint_opts.add_argument(
        "--waypoint-visibility",
        type=int,
        choices=range(4),
        default=0,
        help="waypoint visibility specification",
    )
    return parser.parse_args(sys.argv[1:])


def write_waypoints(args, route):
    # Determine which dimension waypoints will be written to
    match args.structure:
        # End
        case "end_city" | "end_gateway":
            dimension = "dim%1"
        # Nether
        case "ruined_portal_nether" | "fortress" | "bastion_remnant":
            dimension = "dim%-1"
        # Overworld
        case _:
            dimension = "dim%0"

    path = pathlib.Path(args.waypoint_dir, dimension, "mw$default_1.txt")
    structure_name = args.structure.title().replace("_", " ")
    route_name = args.route_name if args.route_name else structure_name

    with open(path, "a") as waypoint_file:
        for idx, loc in enumerate(route):
            structure_waypoint = waypoint.Waypoint(
                name=f"{structure_name} {idx}",
                x=loc[0],
                z=loc[1],
                y="~",
                wp_set=route_name,
                initials=str(idx),
                color=args.waypoint_colour,
                wp_type=args.waypoint_type,
                visibility_type=args.waypoint_visibility,
                destination=False,
                disabled=False,
                rotate_on_tp=False,
                tp_yaw=0,
            )
            waypoint_file.write(f"{structure_waypoint}\n")


def compute_route(args):
    df = pd.read_csv("./structures.txt", header=5, sep=";")
    matching_structures = df[df["structure"] == args.structure]

    if args.details:
        if args.use_regex_in_details:
            matching_structures = matching_structures[
                matching_structures["details"].str.match(args.details, na=False)
            ]
        else:
            matching_structures = matching_structures[
                matching_structures["details"].str.contains(args.details, na=False)
            ]

    X = matching_structures[["x", "z"]].to_numpy()

    np.random.shuffle(X)
    X = np.insert(X, 0, np.array(args.origin), axis=0)

    if args.limit:
        X = X[: args.limit]

    s = np.sum(X**2, axis=1)
    D2 = s[:, None] + s[None, :] - 2 * X @ X.T
    np.maximum(D2, 0, out=D2)
    D = np.sqrt(D2)
    G = nx.from_numpy_array(D)

    return X[np.array(nx_app.christofides(G))]


def get_total_distance(route):
    d = 0.0
    for s, t in zip(route[:-1], route[1:]):
        dist = np.linalg.norm(t - s)
        d += dist
    return d


if __name__ == "__main__":
    args = get_args()
    route = compute_route(args)

    if args.show_total_distance:
        print("Route:")

    [print(*pos, sep="\t") for pos in route]

    if args.show_total_distance:
        print(f"\nDistance:\n{get_total_distance(route):.2f} blocks")

    if args.save_waypoints:
        write_waypoints(args, route)
