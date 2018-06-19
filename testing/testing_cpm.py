from imageAnalysis import handTracking


def try_init_cpm():
    print("Before Init: ")
    print("Kalman Filter: ", handTracking.kalman_filter_array)
    print("Output node: ", handTracking.output_node)
    print("TF Session: ", handTracking.tf_session)
    print("Tracker: ", handTracking.tracker)
    handTracking.init_cpm_session()
    print("After Init: ")
    print("Kalman Filter: ", handTracking.kalman_filter_array)
    print("Output node: ", handTracking.output_node)
    print("TF Session: ", handTracking.tf_session)
    print("Tracker: ", handTracking.tracker)


def main():
    try_init_cpm()


if __name__ == "__main__":
    main()
