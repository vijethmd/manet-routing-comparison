/*
 * Copyright (c) 2009 IITP RAS
 *
 * SPDX-License-Identifier: GPL-2.0-only
 *
 *
 * Authors: Elena Buchatskaia <borovkovaes@iitp.ru>
 *          Pavel Boyko <boyko@iitp.ru>
 */
/*
 * AH-AODV (Adaptive-Hello AODV), Team 11 NP AAT project.
 * Copied from ns-3.48 src/aodv/model/aodv-dpd.cc and renamed (namespace ahaodv) so that it
 * builds next to the standard AODV module; see ah-aodv-routing-protocol.cc for the changes.
 */


#include "ah-aodv-dpd.h"

namespace ns3
{
namespace ahaodv
{

bool
DuplicatePacketDetection::IsDuplicate(Ptr<const Packet> p, const Ipv4Header& header)
{
    return m_idCache.IsDuplicate(header.GetSource(), p->GetUid());
}

void
DuplicatePacketDetection::SetLifetime(Time lifetime)
{
    m_idCache.SetLifetime(lifetime);
}

Time
DuplicatePacketDetection::GetLifetime() const
{
    return m_idCache.GetLifeTime();
}

} // namespace ahaodv
} // namespace ns3
