import React from "react";
import { useContext,useEffect } from "react";
import { Context } from "../store/appContext";

const Cart = function (props) {
  const { store, actions } = useContext(Context);

  useEffect(() => {
    actions.getCart()
  }, [])

  
  console.log(store.products[0])

  return (
    <>
      <div>
      <div className="card mb-3">
            <div className="row g-0">
        <div className="col-md-8">
          <div className="card mb-3">
            <div className="row g-0">
              <div className="col-md-2">
                <img
                  src={props.image}
                  className="img-fluid rounded-start ms-4"
                  style={{
                    width: 150,
                    height: 230,
                  }}
                  alt="..."
                />
              </div>
              <div className="col-md-"> </div>
              <div className="col-md-4">
                <div className="card-body">
                  <h5 className="card-title">
                    <strong>{props.name} </strong>{" "}
                  </h5>{" "}
                  <p className="card-text">{props.description}</p>{" "}
                  <p className="card-text">
                    <small className="text-muted"> Envío: 2 - 4 semanas </small>{" "}
                  </p>{" "}
                  <div className="ui-quantity-selector__container">
                    <input
                      type="submit"
                      value="-"
                      className="cu-button-reset ui-quantity-selector__button"
                      style={{
                        width: 30,
                      }}
                    />{" "}
                    <input
                      type="tel"
                      value="1"
                      className="u-button-reset ui-quantity-selector__input"
                      style={{
                        width: 30,
                      }}
                    />{" "}
                    <input
                      type="submit"
                      value="+"
                      className="cu-button-reset ui-quantity-selector__button"
                      style={{
                        width: 30,
                      }}
                    />{" "}
                  </div>{" "}
                </div>{" "}
              </div>
              <div className="col-md-3"> </div>
              <div className="col-md-2">
                <div className="d-flex align-items-end flex-column">
                  <div className="p-2">
                    {" "}
                    <button className="btn">
                    <i className="fa fa-solid fa-trash"> </i>
                    </button>
                    
                  </div>
                  <div className="mt-auto p-2"> Flex item </div>{" "}
                  <div className="mt-auto p-2"> Flex item </div>{" "}
                </div>
              </div>{" "}
            </div>{" "}
          </div>{" "}
        </div>

        <div className="col-md-4">
          <div className="card mb-3">
            <div className="row g-0">
          <div className="col-md-6">
          <div className="card-body">
              <h5 className="card-title">Productos en el carrito</h5>
              <p className="card-text">
               ahorro aplicado
              </p>
              <h1 className="card-title"> TOTAL</h1>
            </div>
          </div>
          <div className="col-md-6">
          <div className="card-body">
              <h5 className="card-title"> $ 149</h5>
              <p className="card-text">
               $ -25
              </p>
              <h4 className="card-title">$ {props.price}</h4>
             
            </div>
          </div>
          </div>
        </div>
        <div className="col-md-12">
        <div className="card-body">
          
              <a href="#" className="btn btn-primary">
                Alquilar
              </a>
            </div>
        </div>
        </div>

      </div>
      </div>
      </div>
    </>
  );
};

export default Cart;
