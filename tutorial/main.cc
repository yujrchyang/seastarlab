#include <cassert>
#include <iostream>

#include <seastar/core/app-template.hh>
#include <seastar/core/coroutine.hh>
#include <seastar/core/future.hh>
#include <seastar/core/reactor.hh>
#include <seastar/core/sleep.hh>
#include <seastar/coroutine/maybe_yield.hh>

namespace bpo = boost::program_options;

seastar::future<> hello() {
    std::cout << "Hello world\n";
    return seastar::make_ready_future<>();
}

int main(int argc, char **argv) {
    seastar::app_template app;
    std::string run_opt;

    app.add_options()("runopt,o", bpo::value<std::string>(&run_opt)->default_value("hello"),
                      "Specify which function you want test");

    try {
        app.run(argc, argv, [&run_opt] {
            if (run_opt == "hello") {
                return hello();
            } else {
                std::cout << "Invalid option: " << run_opt << "\n";
                return seastar::make_ready_future<>();
            }
        });
    } catch (...) {
        std::cerr << "Couldn't start application: "
                  << std::current_exception()
                  << "\n";
        return 1;
    }
    return 0;
}
