-- License.
-- 
-- Copyright 2018 PingguSoft <pinggusoft@gmail.com>
-- 
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation, either version 3 of the License, or
-- (at your option) any later version.
-- 
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
-- 
-- You should have received a copy of the GNU General Public License
-- along with this program.  If not, see <http://www.gnu.org/licenses/>.
-- 

-- load the udp.port table
udp_table = DissectorTable.get("udp.port")
dissector = udp_table:get_dissector(8889)
if dissector ~= nil then
    udp_table:remove(8889, dissector)
    message("8889 dissector removed")
end

dissector = udp_table:get_dissector(6038)
if dissector ~= nil then
    udp_table:remove(6038, dissector)
    message("6038 dissector removed")
end


-- tello command
-- ts = os.time(os.date("!*t"))
proto_name = "TELLO_CMD"
local tello_cmd = Proto(proto_name, proto_name)

local cmd_names = {
    [17] =   "TELLO_CMD_SSID",
    [18] =   "TELLO_CMD_SET_SSID",
    [19] =   "TELLO_CMD_SSID_PASS",
    [20] =   "TELLO_CMD_SET_SSID_PASS",
    [21] =   "TELLO_CMD_REGION",
    [22] =   "TELLO_CMD_SET_REGION",
    [37] =   "TELLO_CMD_VIDEO_REQ_SPS_PPS",
    [48] =   "TELLO_CMD_TAKE_PICTURE",
    [49] =   "TELLO_CMD_SWITCH_PICTURE_VIDEO",
    [50] =   "TELLO_CMD_START_RECORDING",
    [52] =   "TELLO_CMD_EV",
    [70] =   "TELLO_CMD_DATE_TIME",
    [80] =   "TELLO_CMD_STICK",
    [4176] = "TELLO_CMD_LOG_HEADER_WRITE",
    [4177] = "TELLO_CMD_LOG_DATA_WRITE",
    [4178] = "TELLO_CMD_LOG_CONFIGURATION",
    [26] =   "TELLO_CMD_WIFI_SIGNAL",
    [40] =   "TELLO_CMD_RATE",
    [53] =   "TELLO_CMD_LIGHT_STRENGTH",
    [69] =   "TELLO_CMD_VERSION_STRING",
    [71] =   "TELLO_CMD_ACTIVATION_TIME",
    [73] =   "TELLO_CMD_LOADER_VERSION",
    [86] =   "TELLO_CMD_STATUS",
    [4182] = "TELLO_CMD_ALT_LIMIT",
    [4183] = "TELLO_CMD_LOW_BATT_PARAM",
    [4185] = "TELLO_CMD_ATT_ANGLE",
    [55] =   "TELLO_CMD_JPEG_QUALITY",
    [84] =   "TELLO_CMD_TAKEOFF",
    [85] =   "TELLO_CMD_LANDING",
    [88] =   "TELLO_CMD_SET_HEIHT",
    [92] =   "TELLO_CMD_FLIP",
    [93] =   "TELLO_CMD_THROW_FLY",
    [94] =   "TELLO_CMD_PALM_LANDING",
    [4180] = "TELLO_CMD_PLANE_CALIBRATION",
    [4181] = "TELLO_CMD_LOW_BATTERY_THRESHOLD",
    [4184] = "TELLO_CMD_SET_ATTITUDE_ANGLE",
    [67] =   "TELLO_CMD_ERROR1",
    [68] =   "TELLO_CMD_ERROR2",
    [98] =   "TELLO_CMD_FILE_SIZE",
    [99] =   "TELLO_CMD_FILE_DATA",
    [100 ] = "TELLO_CMD_FILE_COMPLETE",
    [90] =   "TELLO_CMD_HANDLE_IMU_ANGLE",
    [32] =   "TELLO_CMD_SET_VIDEO_BIT_RATE",
    [33] =   "TELLO_CMD_SET_DYN_ADJ_RATE",
    [36] =   "TELLO_CMD_EIS_SETTING",
    [128 ] = "TELLO_CMD_SMART_VIDEO_START",
    [129 ] = "TELLO_CMD_SMART_VIDEO_STATUS",
    [4179] = "TELLO_CMD_BOUNCE",
}

local cmd_fields =
{
    pf_sop     = ProtoField.uint8("tello.sop",     "SOP   ", base.HEX, nil),
    pf_size    = ProtoField.uint16("tello.sz",     "SIZE  "),
    pf_crc8    = ProtoField.uint8("tello.crc8",    "CRC8  ", base.HEX, nil),
    pf_pacType = ProtoField.uint8("tello.pac",     "PACT  ", base.HEX, nil),
    pf_dir     = ProtoField.string("tello.dir",    "DIR   "),
    pf_cmdID   = ProtoField.uint16("tello.cmd",    "CMD   ", base.DEC, cmd_names),
    pf_seqID   = ProtoField.uint16("tello.seq",    "SEQ   "),
    pf_dataSize= ProtoField.uint16("tello.datasz", "DATASZ"),
    pf_data    = ProtoField.bytes("tello.data",    "DATA  ", base.SPACE, nil),
    pf_crc16   = ProtoField.uint16("tello.crc16",  "CRC16 ", base.HEX, nil),
}

tello_cmd.fields = cmd_fields

function tello_cmd.dissector(tvb, pinfo, root)
    pinfo.cols.protocol = "TELLO_CMD"
    local i = 0
    local size = 0
    local stick = 0
    local pktlen = tvb:reported_length_remaining()
    local tree = root:add(tello_cmd, tvb:range(0, pktlen))
    local data_tree;

    sop = tvb(i,1):le_uint()
    if sop == 0xCC then
        tree:add(cmd_fields.pf_sop, tvb(i,1))
        i = i + 1
        tree:add_le(cmd_fields.pf_size, tvb(i,2))
        i = i + 2
        tree:add(cmd_fields.pf_crc8, tvb(i,1))
        i = i + 1
        
        tree:add(cmd_fields.pf_pacType, tvb(i,1))
        pact = tvb(i,1):le_uint()
        i = i + 1
        if bit.band(pact, 0x80) == 0x80 then
            dest = " <- FROM DRONE"
            from_drone = 1
        else
            dest = " -> TO DRONE"
            from_drone = 0
        end
        tree:add(cmd_fields.pf_dir, dest)

        cmd = tvb(i,2):le_uint()
        tree:add_le(cmd_fields.pf_cmdID, tvb(i,2))
        i = i + 2
        
        tree:add_le(cmd_fields.pf_seqID, tvb(i,2))
        i = i + 2
        
        size = tvb:len() - i - 2
        tree:add_le(cmd_fields.pf_dataSize, size)
        if size ~= 0 then
            data_tree = tree:add(cmd_fields.pf_data, tvb(i,size))
            ii = i
-- stick command
            if cmd == 80 then
                stick = tvb(i,6):le_uint64()
                axis1 = stick:band(0x7ff):lower()
                stick = stick:rshift(11)
                axis2 = stick:band(0x7ff):lower()
                stick = stick:rshift(11)
                axis3 = stick:band(0x7ff):lower()
                stick = stick:rshift(11)
                axis4 = stick:band(0x7ff):lower()
                stick = stick:rshift(11)
                axis5 = stick:band(0x7ff):lower()
                
                stick_str = string.format("roll:%4d, pitch:%4d, thr:%4d, yaw:%4d, fastmode:%d", axis1, axis2, axis3, axis4, axis5)
                data_tree:add(tvb(i,size), "STICK - " .. stick_str)
            elseif cmd == 98 and from_drone == 1 then
                fileType = tvb(ii,1):le_uint()
                ii = ii + 1
                fileSize = tvb(ii,4):le_uint()
                ii = ii + 4
                fileID = tvb(ii,2):le_uint()
                ii = ii + 2
                file_str = string.format("fileID:%d, fileType:%d, fileSize:%d", fileID, fileType, fileSize)
                data_tree:add(tvb(i,size), "FILE INFO - " .. file_str)
            elseif cmd == 99 then
                if from_drone == 1 then
                    fileID = tvb(ii,2):le_uint()
                    ii = ii + 2
                    pieceNum = tvb(ii,4):le_uint()
                    ii = ii + 4
                    seqNum = tvb(ii,4):le_uint()
                    ii = ii + 4
                    length = tvb(ii,2):le_uint()
                    file_str = string.format("fileID:%d, pieceNum:%d, seqNum:%d, len:%d", fileID, pieceNum, seqNum, length)
                    data_tree:add(tvb(i,size), "FILE DATA - " .. file_str)
                else
                    ii = ii + 1
                    fileID = tvb(ii,2):le_uint()
                    ii = ii + 2
                    pieceNum = tvb(ii,4):le_uint()
                    ii = ii + 4
                    file_str = string.format("fileID:%d, pieceNum:%d", fileID, pieceNum)
                    data_tree:add(tvb(i,size), "FILE ACK - " .. file_str)
                end
            elseif cmd == 128 then
                if from_drone == 0 then
                    code = tvb(ii, 1):le_uint()
                    start  = bit.band(code, 0x01)
                    code   = bit.rshift(code, 2)
                    mode   = bit.band(code, 0x07)
                    data_tree:add(tvb(i,size), "SMART_REC_CMD - " .. string.format("mode:%d, start:%d", mode, start))
                end
            elseif cmd == 129 then
                if from_drone == 1 then
                    code = tvb(ii, 1):le_uint()
                    dummy  = bit.band(code, 0x07)
                    code   = bit.rshift(code, 3)
                    start  = bit.band(code, 0x03)
                    code   = bit.rshift(code, 2)
                    mode   = bit.band(code, 0x07)
                    data_tree:add(tvb(i,size), "SMART_REC_ACK - " .. string.format("dummy:%d, mode:%d, start:%d", dummy, mode, start))
                end
            end
            
            i = i + size
        end
        tree:add_le(cmd_fields.pf_crc16, tvb(i,2))
        i = i + 2
    end
end


-- tello video
proto_name = "TELLO_VIDEO"
local tello_video = Proto(proto_name, proto_name)
function tello_video.dissector(tvb, pinfo, root)
    pinfo.cols.protocol = "TELLO_VIDEO"

    local i = 0
    local size = 0;
    local tree = root:add(tello_video, tvb(), "TELLO_VIDEO : " .. tvb:len())

    tree:add(tvb(i,1), "SEQ: " .. string.format("%d", tvb(i,1):le_uint()))
    i = i + 1
    subseq = tvb(i,1):le_uint()
    if bit.band(subseq, 0x80) == 0x80 then
        tree:add(tvb(i,1), "SUB: " .. string.format("%d", bit.band(subseq, 0x7f)) .. " Last")
    else
        tree:add(tvb(i,1), "SUB: " .. string.format("%d", bit.band(subseq, 0x7f)))
    end
    
    i = i + 1
    mark = tvb(i,4):le_int();
    i = i + 4
    if mark == 0x01000000 then
        nal_type = bit.band(tvb(i,1):le_uint(), 0x1f)
        tree:add(tvb(i,1), "NAL TYPE: " .. string.format("%d", nal_type))
    end
end

-- register our protocol to handle
udp_table:add(8889, tello_cmd)
udp_table:add(6038, tello_video)