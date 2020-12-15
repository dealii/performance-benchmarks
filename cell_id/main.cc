// ---------------------------------------------------------------------
//
// Copyright (C) 2016 by the deal.II authors
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

#include "../perf.h"

#include <deal.II/base/geometry_info.h>
#include <deal.II/base/logstream.h>
#include <deal.II/grid/tria.h>
#include <deal.II/grid/tria_accessor.h>
#include <deal.II/grid/grid_generator.h>
#include <deal.II/grid/grid_refinement.h>
#include <deal.II/grid/cell_id.h>

#include <fstream>
#include <sstream>

using namespace dealii;

template <int dim>
void check (Triangulation<dim> &tr)
{
  Instrument ii("as_string");
  
  typename Triangulation<dim>::cell_iterator cell = tr.begin(),
                               endc = tr.end();

  unsigned int c = 0;
  
  for (; cell!=endc; ++cell)
    {
      // Store the CellId and create a cell iterator pointing to the same cell

      const CellId cid = cell->id();

      const std::string cids = cid.to_string();
      std::stringstream cidstream(cids);

      CellId cid2;
      cidstream >> cid2;

      typename Triangulation<dim>::cell_iterator cell2 = cid2.to_cell(tr);

      c += cell2->index();
    }
  std::cout << c << std::endl;
}

template <int dim>
void check2 (Triangulation<dim> &tr)
{
  Instrument ii("as_binary");

  typename Triangulation<dim>::cell_iterator cell = tr.begin(),
                               endc = tr.end();

  unsigned int c = 0;
  
  for (; cell!=endc; ++cell)
    {
      // Store the CellId and create a cell iterator pointing to the same cell

      const CellId cid = cell->id();

      const CellId::binary_type cids = cid.to_binary<dim>();

      CellId cid2(cids);

      typename Triangulation<dim>::cell_iterator cell2 = cid2.to_cell(tr);
      c += cell2->index();
    }
  std::cout << c << std::endl;
}


int main ()
{
  MultithreadInfo::set_thread_limit(1);
  Triangulation<2> tria;
  GridGenerator::hyper_cube (tria);
  tria.refine_global (4);
  tria.begin_active()->set_refine_flag();
  tria.execute_coarsening_and_refinement();
  for (unsigned int i = 0; i < 1; ++i)
    {
      check(tria);
      check2(tria);
    }
}
