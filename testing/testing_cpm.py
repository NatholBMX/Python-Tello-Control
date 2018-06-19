from imageAnalysis import handTracking


def test_init_cpm():
    print("Before Init: ", handTracking.tf_session)
    handTracking.init_cpm_session()
    print("After Init: ", handTracking.tf_session)


def main():
    test_init_cpm()


if __name__ == "__main__":
    main()
