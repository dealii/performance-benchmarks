// ---------------------------------------------------------------------
//
// Copyright (C) 2016 - 2020 by the deal.II authors
//
// This file is part of the deal.II library.
//
// The deal.II library is free software; you can use it, redistribute
// it, and/or modify it under the terms of the GNU Lesser General
// Public License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
// The full text of the license can be found in the file LICENSE at
// the top level of the deal.II distribution.
//
// ---------------------------------------------------------------------



// check CellId

#include <deal.II/base/geometry_info.h>
#include <deal.II/base/logstream.h>

#include <deal.II/grid/cell_id.h>
#include <deal.II/grid/grid_generator.h>
#include <deal.II/grid/grid_refinement.h>
#include <deal.II/grid/tria.h>
#include <deal.II/grid/tria_accessor.h>

#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>

#include <fstream>
#include <sstream>

#include "../perf.h"

using namespace dealii;

template <int dim>
void
check_string(const Triangulation<dim> &tr)
{
  Instrument ii("as_string");

  unsigned int c = 0;

  for (const auto &cell : tr.cell_iterators())
    {
      // Store the CellId and create a cell iterator pointing to the same cell

      const CellId cid = cell->id();

      const std::string cids = cid.to_string();

      CellId cid2;
      {
        std::stringstream cidstream(cids);
        cidstream >> cid2;
      }

#if DEAL_II_VERSION_GTE(9, 3, 1)
      const auto cell2 = tr.create_cell_iterator(cid2);
#else
      const auto cell2 = cid2.to_cell(tr);
#endif
      // Do something with the new cell iterator to avoid that optimization
      // could remove the above lines
      c += cell2->index();
    }
  std::cout << c << std::endl;
}

template <int dim>
void
check_binary(const Triangulation<dim> &tr)
{
  Instrument ii("as_binary");

  unsigned int c = 0;

  for (const auto &cell : tr.cell_iterators())
    {
      // Store the CellId and create a cell iterator pointing to the same cell

      const CellId cid = cell->id();

      const CellId::binary_type cids = cid.to_binary<dim>();

      const CellId cid2(cids);

#if DEAL_II_VERSION_GTE(9, 3, 1)
      const auto cell2 = tr.create_cell_iterator(cid2);
#else
      const auto cell2 = cid2.to_cell(tr);
#endif
      // Do something with the new cell iterator to avoid that optimization
      // could remove the above lines
      c += cell2->index();
    }
  std::cout << c << std::endl;
}

template <int dim>
void
check_boost(const Triangulation<dim> &tr)
{
  Instrument ii("via_boost");

  unsigned int c = 0;

  for (const auto &cell : tr.cell_iterators())
    {
      // Store the CellId and create a cell iterator pointing to the same cell

      const CellId cid = cell->id();

      std::stringstream cidstream;
      {
        boost::archive::binary_oarchive oa(cidstream);
        oa &                            cid;
      }

      CellId cid2;
      {
        boost::archive::binary_iarchive ia(cidstream);
        ia &                            cid2;
      }

#if DEAL_II_VERSION_GTE(9, 3, 1)
      const auto cell2 = tr.create_cell_iterator(cid2);
#else
      const auto cell2 = cid2.to_cell(tr);
#endif
      // Do something with the new cell iterator to avoid that optimization
      // could remove the above lines
      c += cell2->index();
    }
  std::cout << c << std::endl;
}

template <int dim>
void
check_utilities(const Triangulation<dim> &tr)
{
  Instrument ii("via_utilities");

  unsigned int c = 0;

  for (const auto &cell : tr.cell_iterators())
    {
      // Store the CellId and create a cell iterator pointing to the same cell

      const CellId cid = cell->id();

      std::vector<char> cids;
      Utilities::pack(cid, cids, /*allow_compression*/ false);

      const CellId cid2 =
        Utilities::unpack<CellId>(cids, /*allow_compression*/ false);

#if DEAL_II_VERSION_GTE(9, 3, 1)
      const auto cell2 = tr.create_cell_iterator(cid2);
#else
      const auto cell2 = cid2.to_cell(tr);
#endif
      // Do something with the new cell iterator to avoid that optimization
      // could remove the above lines
      c += cell2->index();
    }
  std::cout << c << std::endl;
}


int
main()
{
  MultithreadInfo::set_thread_limit(1);
  Triangulation<2> tria;
  GridGenerator::hyper_cube(tria);
  tria.refine_global(4);
  tria.begin_active()->set_refine_flag();
  tria.execute_coarsening_and_refinement();
  for (unsigned int i = 0; i < 1; ++i)
    {
      check_string(tria);
      check_binary(tria);
      check_boost(tria);
      check_utilities(tria);
    }
}
