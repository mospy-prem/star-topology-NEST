# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Base class for all interfaces"""

import logging
from nest.input_validator import input_validator
from nest.input_validator.metric import Bandwidth, Delay, Percentage
from nest.topology.device import Ifb, Device

logger = logging.getLogger(__name__)

# pylint: disable=too-many-public-methods


class BaseInterface:
    """
    Abstraction for an network interface.

    Attributes
    ----------
    name : str
        User given name for the interface
    id : str
        This value is used by `engine` to create emulated interface
        entity
    node : Node
        `Node` which contains this `Interface`
    address : str/Address
        IP address assigned to this interface
    """

    @input_validator
    def __init__(self, interface_name: str, device: Device):
        """
        Constructor of BaseInterface.

        Parameters
        ----------
        interface_name : str
            Name of the interface
        """

        self._name = interface_name
        self._device = device
        self._ifb = None

        # Track bandwidth and delay
        self._bandwidth = None
        self._delay = None

    @property
    def name(self):
        """Getter for name"""
        return self._device.name

    @property
    def id(self):
        """Getter for id"""
        return self._device.id

    @property
    def node_id(self):
        """
        Getter for the `Node` associated
        with the interface
        """
        return self._device.node_id

    @node_id.setter
    def node_id(self, node_id):
        """
        Setter for the `Node` associated
        with the interface

        Parameters
        ----------
        node : Node
            The node where the interface is to be installed
        """
        self._device.node_id = node_id

    @property
    def ifb_id(self):
        """
        Getter for the id of the ifb of
        the interface
        """
        return self._ifb.id

    @property
    def address(self):
        """
        NOTE: This method is deprecated and will be removed in future versions.
              Use get_address method instead.

        Getter for the address associated
        with the interface
        """
        return self._device.get_address()

    @address.setter
    def address(self, address):
        """
        NOTE: This method is deprecated and will be removed in future versions.
              Use set_address method instead.

        Assigns IP address to an interface

        Parameters
        ----------
        address : Address/str or List[Address/str]
            IP address to be assigned to the interface
        """
        self._device.set_address(address)

    def set_address(self, address):
        """
        Assigns IP addresses to an interface

        Parameters
        ----------
        address : Address/str or List[Address/str]
            IP address to be assigns to the interface
        """
        self._device.set_address(address)

    def add_address(self, address):
        """
        Adds IP addresses to an interface

        Parameters
        ----------
        address : Address/str or List[Address/str]
            IP address to be added to the interface
        """
        self._device.add_address(address)

    def del_address(self, address):
        """
        Delete IP address(es) from the interface

        Parameters
        ----------
        address : str or list
            IP address to be deleted from the interface
        """
        self._device.del_address(address)

    def enable_mpls(self):
        """
        Enables mpls input through the interface.
        Requires mpls kernel modules to be loaded.

        Run ``sudo modprobe mpls_iptunnel`` to load mpls modules.
        """
        self._device.enable_mpls()

    def is_mpls_enabled(self):
        """
        Check if the interface has mpls enabled
        """
        return self._device.is_mpls_enabled()

    @property
    def mtu(self):
        """
        Get the maximum transmit unit value for the interface
        """
        return self._device.mtu

    @mtu.setter
    def mtu(self, mtu_value):
        """
        Set the maximum transmit unit value for the interface
        Default is 1500 bytes.
        """
        self._device.mtu = mtu_value

    @input_validator
    def get_address(self, ipv4: bool = True, ipv6: bool = True, as_list: bool = False):
        """
        Gets the required IP addresses for the interface
        Returns a list or an Address object

        Parameters
        ----------
        ipv4 : If set to true, the IPv4 address of the interface is returned (defaults to True)
        ipv6 : If set to true, the IPv6 address of the interface is returned (defaults to True)
        If both are True, both the addresses are returned
        Either ipv4 or ipv6 must be True
        as_list : Only applicable when a single address is set (Applicable individually for
                  ipv4 and ipv6).
        Returns Address object when false, else returns a single Address object in list
        (defaults to False).
        """
        return self._device.get_address(ipv4, ipv6, as_list)

    def disable_ip_dad(self):
        """
        Disables Duplicate addresses Detection (DAD) for an interface.
        """
        self._device.disable_ip_dad()

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        Parameters
        ----------
        mode : string
            interface mode to be set
        """
        self._device.set_mode(mode)

    def get_qdisc(self):
        """
        Note that this is the qdisc set inside
        the IFB.
        """
        if self._ifb is not None:
            for qdisc in self._ifb.qdisc_list:
                if qdisc.parent == "1:1" and qdisc.handle == "11:":
                    return qdisc
        return None

    def _create_and_mirred_to_ifb(self):
        """
        Creates a IFB for the interface so that a Qdisc can be
        installed on it
        Mirrors packets to be sent out of the interface first to
        itself (IFB)
        Assumes the interface has already invoked _set_structure()

        Parameters
        ----------
        """

        ifb_name = "ifb-" + self.name
        self._ifb = Ifb(ifb_name, self.node_id, self.id)

    @input_validator
    def set_bandwidth(self, bandwidth: Bandwidth):
        """
        Sets a minimum bandwidth for the interface
        It is done by adding a HTB qdisc and a rate parameter to the class

        Parameters
        ----------
        bandwidth : Bandwidth
            The minimum rate that has to be set in kbit
        """

        self._device.set_structure()
        self._bandwidth = bandwidth.string_value

        bandwidth_parameter = {"rate": bandwidth.string_value}

        self._device.change_class("htb", "1:", "1:1", **bandwidth_parameter)

    @input_validator
    def set_delay(self, delay: Delay):
        """
        Adds a delay to the link between two namespaces
        It is done by adding a delay in the interface

        Parameters
        ----------
        delay : Delay
            The delay to be added
        """
        # TODO: Make adding delay possible without bandwidth being set

        self._device.set_structure()
        self._delay = delay

        delay_parameter = {"delay": delay.string_value}

        self._device.change_qdisc("11:", "netem", **delay_parameter)

    @input_validator
    def set_packet_corruption(
        self, corrupt_rate: Percentage, correlation_rate: Percentage = None
    ):
        """
        allows the emulation of random noise introducing an error in a
        random position for a chosen percent of packets.
        It is also possible to add a correlation.

        Parameters
        ----------
        corrupt_rate : str
            rate of the packets to be corrupted
        correlation_rate : str
            correlation between the corrupted packets
        """
        parsed_correlation_rate = (
            correlation_rate.string_value if correlation_rate else ""
        )

        self._device.set_structure()

        corrupt_parameter = {
            "corrupt": corrupt_rate.string_value,
            "": parsed_correlation_rate,
        }

        self._device.change_qdisc("11:", "netem", **corrupt_parameter)

    @input_validator
    def set_packet_loss(
        self, loss_rate: Percentage, correlation_rate: Percentage = None
    ):
        """
        adds an independent loss probability to the packets outgoing from
        the chosen network interface.
        It is also possible to add a correlation

        Parameters
        ----------
        loss_rate : str
            rate of the packets to be lost
        correlation_rate : str
            correlation between the lost packets
        """
        parsed_correlation_rate = (
            correlation_rate.string_value if correlation_rate else ""
        )

        self._device.set_structure()

        loss_parameter = {"loss": loss_rate.string_value, "": parsed_correlation_rate}

        self._device.change_qdisc("11:", "netem", **loss_parameter)

    @input_validator
    def set_packet_duplication(self, duplicate_rate: Percentage):
        """
        Using this option the chosen percent of packets is duplicated
        before queuing them.

        Paramters
        ----------
        duplicate_rate: Percentage
            rate of packets to get duplicated.

        """

        self._device.set_structure()

        duplicate_parameter = {"duplicate": duplicate_rate.string_value}

        self._device.change_qdisc("11:", "netem", **duplicate_parameter)

    @input_validator
    def set_packet_reordering(
        self, delay: Delay, reorder_rate: Percentage, gap: int = None
    ):
        """
        Adds reordering of packets configured on qdisc to outgoing packets
        from one host to another.

        Parameter
        ---------
        delay: Delay
            Delay to be added for packet reordering
        reorder_rate: Percentage
            Percentage of packets to reorder
        gap : int (Optional)
            (gap - 1) packets will be delayed, and subsequent packets
            will be sent immediately.
        """

        new_delay = delay + self._delay

        reorder_parameter = {
            "delay": new_delay.string_value,
            "reorder": reorder_rate.string_value,
        }

        if gap is not None:
            reorder_parameter["gap"] = str(gap)

        self._device.set_structure()

        self._device.change_qdisc("11:", "netem", **reorder_parameter)

    def set_qdisc(self, qdisc, **kwargs):
        """
        Adds the Queueing algorithm to the interface

        Parameters
        ----------
        qdisc : string
            The Queueing algorithm to be added
        bandwidth :
            Link bandwidth
        """

        qdisc_list = ["choke", "codel", "fq_codel", "pie", "fq_pie", "pfifo", "red"]

        if qdisc not in qdisc_list:
            raise ValueError(f"{qdisc} is not a valid Qdisc")

        self._device.set_structure()

        if self._ifb is None:
            self._create_and_mirred_to_ifb()

        if self._bandwidth is not None:
            self._ifb.set_bandwidth(self._bandwidth)

        self._ifb.delete_qdisc("11:")
        self._ifb.add_qdisc(qdisc, "1:1", "11:", **kwargs)

    @input_validator
    def set_attributes(
        self, bandwidth: Bandwidth, delay: Delay, qdisc: str = None, **kwargs
    ):
        """
        Add attributes bandwidth, delay and qdisc to interface

        Parameters
        ----------
        bandwidth : str/Bandwidth
            Packet outgoing rate
        delay : str/Delay
            Delay before packet is sent out
        qdisc : string
            The Queueing algorithm to be added to interface
            (Default value = None)
        """

        self.set_bandwidth(bandwidth)
        self.set_delay(delay)

        if qdisc is not None:
            self.set_qdisc(qdisc, **kwargs)

    def enable_offload(self, offload_name):
        """
        API for enabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to enable
        """

        self._device.enable_offload(offload_name)

    def disable_offload(self, offload_name):
        """
        API for disabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to disable
        """

        self._device.disable_offload(offload_name)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"
